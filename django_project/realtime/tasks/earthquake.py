# coding=utf-8
from __future__ import absolute_import

import json
import logging
import os
import urllib2
from urlparse import urljoin

from bs4 import BeautifulSoup
from celery import chain
from django.conf import settings
from django.core.files import File
from django.core.urlresolvers import reverse

from core.celery_app import app
from realtime.app_settings import LOGGER_NAME, FELT_EARTHQUAKE_URL, \
    EARTHQUAKE_EXPOSURES, EARTHQUAKE_AGGREGATION, \
    EARTHQUAKE_REPORT_TEMPLATE, \
    EARTHQUAKE_LAYER_ORDER, GRID_FILE_DEFAULT_NAME
from realtime.helpers.inaware import InAWARERest
from realtime.models.earthquake import Earthquake, EarthquakeReport
from realtime.tasks.headless.inasafe_wrapper import \
    run_multi_exposure_analysis, generate_report, RESULT_SUCCESS
from realtime.utils import zip_inasafe_analysis_result, substitute_layer_order

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '3/15/16'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(queue='inasafe-django', default_retry_delay=10 * 60, bind=True)
def push_shake_to_inaware(self, shake_id, source_type):
    """

    :param self: Required parameter if bind=True is used

    :param shake_id: The shake id of the event
    :type shake_id: str
    :return:
    """
    try:
        inaware = InAWARERest()
        hazard_id = inaware.get_hazard_id(shake_id)
        if not hazard_id:
            # hazard id is not there?
            # then BMKG haven't pushed it yet to InaWARE then
            raise Exception('Hazard id is none: %s' % shake_id)
        pdf_url = reverse('realtime_report:report_pdf', kwargs={
            'shake_id': shake_id,
            'source_type': source_type,
            'language': 'en',
            'language2': 'en',
        })
        pdf_url = urljoin(
            settings.SITE_DOMAIN_NAME,
            pdf_url)
        inaware.post_url_product(
            hazard_id, pdf_url, 'InaSAFE Estimated Earthquake Impact - EN')
        pdf_url = reverse('realtime_report:report_pdf', kwargs={
            'shake_id': shake_id,
            'source_type': source_type,
            'language': 'id',
            'language2': 'id',
        })
        pdf_url = urljoin(
            settings.SITE_DOMAIN_NAME,
            pdf_url)
        inaware.post_url_product(
            hazard_id, pdf_url, 'InaSAFE Perkiraan Dampak Gempa - ID')

    except ValueError as exc:
        LOGGER.debug(exc)

    except Exception as exc:
        # retry in 30 mins
        LOGGER.debug(exc)
        raise self.retry(exc=exc, countdown=30 * 60)


@app.task(queue='inasafe-django')
def retrieve_felt_earthquake_list():
    """Retrieve felt earthquake list from BMKG website

    Executed once in an hour

    :return:
    """
    # Scraped from BMKG's web
    target_url = FELT_EARTHQUAKE_URL
    try:
        response = urllib2.urlopen(target_url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        trs = soup.table.tbody.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            event_id = tds[5].a['data-target'][1:]
            try:
                shake = Earthquake.objects.get(shake_id=event_id)
                shake.felt = True
                shake.save()
            except Earthquake.DoesNotExist:
                pass
    except urllib2.URLError:
        LOGGER.debug('Failed to connect to {url}'.format(url=target_url))


@app.task(queue='inasafe-django')
def generate_event_report(earthquake_event):
    """Generate Earthquake report

    :param earthquake_event: Earthquake event instance
    :type earthquake_event: Earthquake
    :return:
    """
    if not earthquake_event.hazard_layer_exists:

        # Skip all process if exists
        return

    # Check raw hazard stored
    elif not earthquake_event.shake_grid_xml:

        earthquake_event.refresh_from_db()

        # Store Grid XML from hazard path into db
        if earthquake_event.shake_grid:
            shake_grid_xml = earthquake_event.shake_grid.read()

        # Attempt to get grid.xml by guessing from hazard path
        else:
            dir_name = os.path.dirname(earthquake_event.hazard_path)
            grid_path = os.path.join(dir_name, GRID_FILE_DEFAULT_NAME)
            with open(grid_path) as f:
                shake_grid_xml = f.read()

        # Use save to trigger signals again
        Earthquake.objects.filter(
            id=earthquake_event.id).update(
            shake_grid_xml=shake_grid_xml)

        earthquake_event.refresh_from_db()

        # Remove un-needed Grid XML
        if earthquake_event.shake_grid:
            earthquake_event.shake_grid.delete(save=False)

        earthquake_event.save()

    # Check impact layer
    elif (not earthquake_event.impact_layer_exists and
            earthquake_event.need_run_analysis):

        # If hazard exists but impact layer is not, then create a new analysis
        # job.
        run_earthquake_analysis(earthquake_event)

    # Check report
    elif (not earthquake_event.has_reports and
            earthquake_event.need_generate_reports):

        # If analysis is done but report doesn't exists, then create the
        # reports.
        generate_earthquake_report(earthquake_event)


def run_earthquake_analysis(event):
    """Run analysis.

    :param event: event instance
    :type event: Earthquake
    """
    event.refresh_from_db()
    hazard_layer_uri = event.hazard_path

    tasks_chain = chain(
        # Run multi exposure analysis
        run_multi_exposure_analysis.s(
            hazard_layer_uri,
            EARTHQUAKE_EXPOSURES,
            EARTHQUAKE_AGGREGATION,
        ).set(queue=run_multi_exposure_analysis.queue),

        # Handle analysis products
        handle_analysis.s(
            event.id
        ).set(queue=handle_analysis.queue),
    )

    @app.task
    def _handle_error(req, exc, traceback):
        """Update task status as Failure."""
        Earthquake.objects.filter(id=event.id).update(
            analysis_task_status='FAILURE')

    async_result = tasks_chain.apply_async(link_error=_handle_error.s())
    Earthquake.objects.filter(id=event.id).update(
        analysis_task_id=async_result.task_id,
        analysis_task_status=async_result.state)


@app.task(queue='inasafe-django')
def handle_analysis(analysis_result, event_id):
    """Handle analysis products"""
    earthquake = Earthquake.objects.get(id=event_id)

    task_state = 'FAILURE'
    if analysis_result['status'] == RESULT_SUCCESS:
        try:
            earthquake.impact_file_path = analysis_result[
                'output']['analysis_summary']
            earthquake.mmi_output_path = analysis_result[
                'output']['population']['earthquake_contour']

            # Zip result
            zip_inasafe_analysis_result(earthquake.impact_file_path)
            task_state = 'SUCCESS'
        except BaseException as e:
            LOGGER.exception(e)
    else:
        LOGGER.error(analysis_result['message'])

    earthquake.analysis_task_status = task_state
    earthquake.analysis_task_result = json.dumps(analysis_result)
    earthquake.save()

    return analysis_result


def generate_earthquake_report(event):
    """Generate report for event.

    :param event: event instance
    :type event: Earthquake
    """
    event.refresh_from_db()
    impact_layer_uri = event.impact_file_path

    analysis_result = json.loads(event.analysis_task_result)

    source_dict = dict(analysis_result['output'])
    source_dict.update({
        'hazard': event.hazard_path
    })

    layer_order = substitute_layer_order(
        EARTHQUAKE_LAYER_ORDER, source_dict)

    tasks_chain = chain(
        # Generate report
        generate_report.s(
            impact_layer_uri, EARTHQUAKE_REPORT_TEMPLATE, layer_order
        ).set(queue=generate_report.queue),

        # Handle report
        handle_report.s(
            event.id
        ).set(queue=handle_report.queue)
    )

    @app.task
    def _handle_error(req, exc, traceback):
        """Update task status as Failure."""
        Earthquake.objects.filter(id=event.id).update(
            report_task_status='FAILURE')

    async_result = tasks_chain.apply_async(link_error=_handle_error.s())

    Earthquake.objects.filter(id=event.id).update(
        report_task_id=async_result.task_id,
        report_task_status=async_result.state)


@app.task(queue='inasafe-django')
def handle_report(report_result, event_id):
    """Handle report product"""
    earthquake = Earthquake.objects.get(id=event_id)

    # Set the report path if success
    task_state = 'FAILURE'
    if report_result['status'] == RESULT_SUCCESS:
        try:
            # Create earthquake report object
            # Set the language manually first
            earthquake_report = EarthquakeReport(
                earthquake=earthquake, language='en')

            report_path = report_result[
                'output']['pdf_product_tag']['realtime-earthquake-en']
            with open(report_path, 'rb') as report_file:
                earthquake_report.report_pdf.save(
                    earthquake_report.report_map_filename,
                    File(report_file),
                    save=True)
                earthquake.refresh_from_db()
            task_state = 'SUCCESS'
        except BaseException as e:
            LOGGER.exception(e)
    else:
        LOGGER.error(report_result['message'])

    Earthquake.objects.filter(id=earthquake.id).update(
        report_task_status=task_state,
        report_task_result=json.dumps(report_result))

    return report_result
