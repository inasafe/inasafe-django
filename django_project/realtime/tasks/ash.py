# coding=utf-8
from __future__ import absolute_import

import logging
import os
import shutil
from tempfile import mkdtemp

import pytz
from celery.result import AsyncResult, allow_join_result

from core.celery_app import app

from realtime.app_settings import LOGGER_NAME, REALTIME_HAZARD_DROP
from realtime.models.ash import Ash
from realtime.tasks.realtime.ash import process_ash
from realtime.tasks.realtime.celery_app import app as realtime_app
from realtime.tasks.headless.celery_app import app as headless_app

from realtime.tasks.headless.inasafe_wrapper import (
    run_multi_exposure_analysis, generate_report)

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '20/7/17'


LOGGER = logging.getLogger(LOGGER_NAME)

ASH_EXPOSURES = [
    '/home/headless/contexts/ash/exposure/IDN_Airport_OpenFlights_WGS84.shp',
    '/home/headless/contexts/contexts/ash/exposure/IDN_Landcover_250K_WGS84'
    '.shp',

    '/home/headless/contexts/common/exposure/'
    'IDN_Capital_Population_Point_WGS84.shp'
]
ASH_AGGREGATION = ''
ASH_REPORT_TEMPLATE = '/home/headless/qgis-templates/realtime-ash-en.qpt'
ASH_LAYER_ORDER = [
    '/home/headless/contexts/ash/exposure/IDN_Airport_OpenFlights_WGS84.shp',
    # the ash layer
    '/home/headless/contexts/common/context/hillshade.tif'
]


@app.task(queue='inasafe-django')
def check_processing_task():
    for ash in Ash.objects.exclude(
            task_id__isnull=True).exclude(
            task_id__exact='').exclude(
            task_status__iexact='SUCCESS'):
        task_id = ash.task_id
        result = AsyncResult(id=task_id, app=realtime_app)
        if ash.task_status != result.state:
            status_changed = True
        else:
            status_changed = False
        ash.task_status = result.state
        if status_changed:
            ash.hazard_path = ash.hazard_file.path
        ash.save()
    for ash in Ash.objects.exclude(
            analysis_task_id__isnull=True).exclude(
            analysis_task_id__exact='').exclude(
            analysis_task_status__iexact='SUCCESS'):
        task_id = ash.task_id
        result = AsyncResult(id=task_id, app=headless_app)
        ash.task_status = result.state
        ash.save()


@app.task(queue='inasafe-django')
def generate_event_report(ash_event):
    """Generate Ash Report

    :param ash_event: Ash event instance
    :type ash_event: Ash
    :return:
    """
    ash_event.use_timezone()

    if ash_event.event_time.tzinfo:
        event_time = ash_event.event_time
    else:
        event_time = ash_event.event_time.replace(tzinfo=pytz.utc)

    if not ash_event.hazard_layer_exists:

        # For ash realtime we need to make sure hazard file is processed.
        # Because the hazard raw data comes from user upload

        # copy hazard data realtime location
        hazard_drop_path = mkdtemp(dir=REALTIME_HAZARD_DROP)
        hazard_drop_path = os.path.join(
            hazard_drop_path, os.path.basename(ash_event.hazard_file.path))
        shutil.copy(ash_event.hazard_file.path, hazard_drop_path)

        LOGGER.info('Sending task ash hazard processing.')
        result = process_ash.delay(
            ash_file_path=hazard_drop_path,
            volcano_name=ash_event.volcano.volcano_name,
            region=ash_event.volcano.province,
            latitude=ash_event.volcano.location[1],
            longitude=ash_event.volcano.location[0],
            alert_level=ash_event.alert_level,
            event_time=event_time,
            eruption_height=ash_event.eruption_height,
            vent_height=ash_event.volcano.elevation,
            forecast_duration=ash_event.forecast_duration)

        # with allow_join_result():
        #     task_result = result.get()
        #
        #     success = task_result.get('success')
        #     hazard_path = task_result.get('hazard_path')
        #
        # if not success:
        #     raise Exception('Error Generating Hazard file.')
        #
        # ash_event.hazard_path = hazard_path
        # Ash.objects.filter(id=ash_event.id).update(hazard_path=hazard_path)
        Ash.objects.filter(id=ash_event.id).update(
            task_id=result.task_id,
            task_status=result.state)

    # TODO: Generate Ash report
    # elif not ash_event.impact_file_path:
    #     with allow_join_result():
    #         async_analysis_result = run_ash_analysis(ash_event.id)
    #         analysis_result = async_analysis_result.get()
    #         if analysis_result['status'] == 0:
    #             impact_layer_path = analysis_result.get('output', {}).get(
    #                 'analysis_summary')
    #             Ash.objects.filter(id=ash_event.id).update(
    #                 impact_file_path=impact_layer_path)
    #             async_report_result = generate_ash_report(ash_event.id)
    #             report_result = async_report_result.get()
    #             if report_result['status'] == 0:
    #                 pass
    #             else:
    #                 LOGGER.debug('Generate ash report failed.')

    # TODO: Save Ash products to databases

@app.task(queue='inasafe-django')
def run_ash_analysis(ash_event):
    """Run ash analysis and get report from it.

    :param ash_event: Ash event instance
    :type ash_event: Ash
    """
    ash_layer_uri = ash_event.hazard_path
    async_result = run_multi_exposure_analysis.delay(
        ash_layer_uri,
        ASH_EXPOSURES,
        ASH_AGGREGATION,
    )
    Ash.objects.filter(id=ash_event.id).update(
        analysis_task_id=async_result.task_id,
        analysis_task_status=async_result.state)


def generate_ash_report(ash_id):
    """Generate ash report for ash_id.

    :param ash_id: The id of the ash object.
    :type ash_id: int
    """
    ash = Ash.objects.get(pk=ash_id)
    ash_impact_layer_uri = ash.impact_file_path
    layer_order = [
        ASH_LAYER_ORDER[0],
        ash.hazard_path,
        ASH_LAYER_ORDER[1]
    ]
    async_result = generate_report.delay(
        ash_impact_layer_uri, ASH_REPORT_TEMPLATE, layer_order)
    return async_result
