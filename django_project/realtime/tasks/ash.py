# coding=utf-8
from __future__ import absolute_import

import json
import logging
import os
import shutil
from tempfile import mkdtemp

import pytz
from celery import chain
from django.core.files import File

from core.celery_app import app
from realtime.app_settings import LOGGER_NAME, REALTIME_HAZARD_DROP, \
    ASH_LAYER_ORDER, ASH_EXPOSURES, ASH_AGGREGATION, ASH_HAZARD_TYPE
from realtime.models.ash import Ash
from realtime.tasks import get_keywords
from realtime.tasks.headless.inasafe_wrapper import (
    run_multi_exposure_analysis, generate_report, RESULT_SUCCESS)
from realtime.tasks.realtime.ash import process_ash
from realtime.utils import substitute_layer_order, template_names, \
    template_paths
from realtime.tasks.geonode import (
    upload_layer_to_geonode, handle_push_to_geonode)

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '20/7/17'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(queue='inasafe-django')
def generate_hazard_layer(ash_event):
    """Generate hazard layer from raw hazard file.

    :param ash_event: Ash event instance
    :type ash_event: Ash
    :return:
    """
    ash_event.use_timezone()

    if ash_event.event_time.tzinfo:
        event_time = ash_event.event_time
    else:
        event_time = ash_event.event_time.replace(tzinfo=pytz.utc)

    # For ash realtime we need to make sure hazard file is processed.
    # Because the hazard raw data comes from user upload

    # copy hazard data realtime location
    hazard_drop_path = mkdtemp(dir=REALTIME_HAZARD_DROP)
    hazard_drop_path = os.path.join(
        hazard_drop_path, os.path.basename(ash_event.hazard_file.path))
    shutil.copy(ash_event.hazard_file.path, hazard_drop_path)

    LOGGER.info('Sending task ash hazard processing.')

    tasks_chain = chain(
        # Generate hazard data
        process_ash.s(
            ash_file_path=hazard_drop_path,
            volcano_name=ash_event.volcano.volcano_name,
            region=ash_event.volcano.province,
            latitude=ash_event.volcano.location[1],
            longitude=ash_event.volcano.location[0],
            alert_level=ash_event.alert_level,
            event_time=event_time,
            eruption_height=ash_event.eruption_height,
            vent_height=ash_event.volcano.elevation,
            forecast_duration=ash_event.forecast_duration
        ).set(queue=process_ash.queue),

        # Handle hazard process
        handle_hazard_process.s(
            event_id=ash_event.id
        ).set(queue=handle_hazard_process.queue),

        # # Push to GeoNode
        upload_layer_to_geonode.s(
            event_id=ash_event.id
        ).set(queue=upload_layer_to_geonode.queue),
        #
        # # Handle push to geonode process
        handle_push_to_geonode.s(
            event_id=ash_event.id
        ).set(queue=handle_push_to_geonode.queue)
    )

    @app.task
    def _handle_error(req, exc, traceback):
        """Update task status as Failure."""
        Ash.objects.filter(id=ash_event.id).update(
            task_status='FAILURE')

    result = tasks_chain.apply_async()

    Ash.objects.filter(id=ash_event.id).update(
        task_id=result.task_id,
        task_status=result.state)


@app.task(queue='inasafe-django')
def generate_event_report(ash_event, locale='en'):
    """Generate Ash Report

    :param ash_event: Ash event instance
    :type ash_event: Ash
    :return:
    """
    ash_event.use_timezone()
    ash_event.inspected_language = locale

    # Check impact layer
    if (ash_event.hazard_layer_exists and
            not ash_event.impact_layer_exists and
            ash_event.need_run_analysis):

        # If hazard exists but impact layer is not, then create a new analysis
        # job.
        run_ash_analysis(ash_event, locale)

    # Check report
    elif (ash_event.hazard_layer_exists and
          ash_event.impact_layer_exists and
          not ash_event.has_reports and
          ash_event.need_generate_reports):

        # If analysis is done but report doesn't exists, then create the
        # reports.
        generate_ash_report(ash_event, locale)


@app.task(queue='inasafe-django')
def handle_hazard_process(process_result, event_id):
    """Handle hazard generation."""
    task_state = 'FAILURE'
    try:
        if process_result['success']:
            task_state = 'SUCCESS'
    except BaseException as e:
        LOGGER.exception(e)

    Ash.objects.filter(id=event_id).update(
        task_status=task_state)
    ash = Ash.objects.get(id=event_id)
    ash.task_status = task_state
    ash.save()

    return process_result


def run_ash_analysis(ash_event, locale='en'):
    """Run ash analysis.

    :param ash_event: Ash event instance
    :type ash_event: Ash
    """
    ash_event.refresh_from_db()
    ash_event.inspected_language = locale
    hazard_layer_uri = ash_event.hazard_path

    tasks_chain = chain(
        # Run multi exposure analysis
        run_multi_exposure_analysis.s(
            hazard_layer_uri,
            ASH_EXPOSURES,
            ASH_AGGREGATION,
            locale=locale
        ).set(queue=run_multi_exposure_analysis.queue),

        # Handle analysis products
        handle_analysis.s(
            ash_event.id,
            locale=locale
        ).set(queue=handle_analysis.queue)
    )

    @app.task
    def _handle_error(req, exc, traceback):
        """Update task status as Failure."""
        ash_event.analysis_task_status = 'FAILURE'

    async_result = tasks_chain.apply_async()
    ash_event.analysis_task_id = async_result.task_id
    ash_event.analysis_task_status = async_result.state


@app.task(queue='inasafe-django')
def handle_analysis(analysis_result, event_id, locale='en'):
    """Handle analysis products"""
    ash = Ash.objects.get(id=event_id)
    ash.inspected_language = locale

    task_state = 'FAILURE'
    if analysis_result['status'] == RESULT_SUCCESS:
        try:
            ash.impact_file_path = analysis_result[
                'output']['analysis_summary']
            task_state = 'SUCCESS'

            chain(
                get_keywords.s(
                    ash.impact_file_path,
                    keyword='keyword_version'
                ).set(queue=get_keywords.queue),

                handle_keyword_version.s(
                    ash.id
                ).set(queue=handle_keyword_version.queue)

            ).delay()
        except BaseException as e:
            LOGGER.exception(e)
    else:
        LOGGER.error(analysis_result['message'])

    ash.analysis_task_status = task_state
    ash.analysis_task_result = json.dumps(analysis_result)
    ash.save()

    return analysis_result


def generate_ash_report(ash_event, locale='en'):
    """Generate ash report for ash event.

    :param ash_event: Ash event instance
    :type ash_event: Ash
    """
    LOGGER.info('Generate Ash Report {0}'.format(locale))
    ash_event.refresh_from_db()
    ash_event.inspected_language = locale
    impact_layer_uri = ash_event.impact_file_path

    analysis_result = json.loads(ash_event.analysis_task_result)

    source_dict = dict(analysis_result['output'])
    source_dict.update({
        'hazard': ash_event.hazard_path
    })

    layer_order = substitute_layer_order(
        ASH_LAYER_ORDER, source_dict)

    report_template = template_paths(ASH_HAZARD_TYPE, locale)

    tasks_chain = chain(
        # Generate report
        generate_report.s(
            impact_layer_uri, report_template, layer_order,
            locale=locale
        ).set(queue=generate_report.queue),

        # Handle report
        handle_report.s(
            ash_event.id,
            locale=locale
        ).set(queue=handle_report.queue)
    )

    @app.task
    def _handle_error(req, exc, traceback):
        """Update task status as Failure."""
        ash_event.report_task_status = 'FAILURE'

    async_result = tasks_chain.apply_async()

    ash_event.report_task_id = async_result.task_id
    ash_event.report_task_status = async_result.status


@app.task(queue='inasafe-django')
def handle_report(report_result, event_id, locale='en'):
    """Handle report product"""
    ash = Ash.objects.get(id=event_id)
    ash.inspected_language = locale
    report_object = ash.report_object
    template_name = template_names(ASH_HAZARD_TYPE, locale)

    # Set the report path if success
    task_state = 'FAILURE'
    if report_result['status'] == RESULT_SUCCESS:
        try:
            report_path = report_result[
                'output']['pdf_product_tag'][template_name]
            with open(report_path, 'rb') as report_file:
                report_object.report_map.save(
                    report_object.report_map_filename,
                    File(report_file),
                    save=True)
                ash.refresh_from_db()
            task_state = 'SUCCESS'
        except BaseException as e:
            LOGGER.exception(e)
    else:
        LOGGER.error(report_result['message'])

    report_object.report_task_status = task_state
    report_object.report_task_result = json.dumps(report_result)
    report_object.save()

    return report_result


@app.task(queue='inasafe-django')
def handle_keyword_version(version, event_id):
    """Handle keyword version."""
    event = Ash.objects.get(id=event_id)
    """:type: Earthquake"""
    event.inasafe_version = version
    event.save()
