# coding=utf-8
from __future__ import absolute_import

import logging
import urllib2
from urlparse import urljoin

import os
from bs4 import BeautifulSoup
from celery.result import AsyncResult
from django.conf import settings
from django.core.files import File
from django.core.urlresolvers import reverse

from core.celery_app import app
from realtime.app_settings import LOGGER_NAME, FELT_EARTHQUAKE_URL, \
    EARTHQUAKE_EXPOSURES, EARTHQUAKE_AGGREGATION, EARTHQUAKE_REPORT_TEMPLATE, \
    EARTHQUAKE_LAYER_ORDER, GRID_FILE_DEFAULT_NAME
from realtime.helpers.inaware import InAWARERest
from realtime.models.earthquake import Earthquake, EarthquakeReport
from realtime.tasks.headless.celery_app import app as headless_app
from realtime.tasks.headless.inasafe_wrapper import \
    run_multi_exposure_analysis, generate_report

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '3/15/16'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(queue='inasafe-django', default_retry_delay=10 * 60, bind=True)
def push_shake_to_inaware(self, shake_id):
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
def check_processing_task():
    # Checking analysis task
    for earthquake in Earthquake.objects.exclude(
            analysis_task_id__isnull=True).exclude(
            analysis_task_id__exact='').filter(
            analysis_task_status__iexact='PENDING'):
        analysis_task_id = earthquake.analysis_task_id
        result = AsyncResult(id=analysis_task_id, app=headless_app)
        # Set the impact file path if success
        # Set impact file path if success
        if result.state == 'SUCCESS':
            task_state = 'FAILURE'
            try:
                earthquake.impact_file_path = result.result[
                    'output']['analysis_summary']
                task_state = 'SUCCESS'
            except BaseException as e:
                LOGGER.exception(e)

            earthquake.analysis_task_status = task_state
            earthquake.save()
        elif result.state == 'FAILURE':
            Earthquake.objects.filter(id=earthquake.id).update(
                analysis_task_id=result.state)

    # Checking report generation task
    for earthquake in Earthquake.objects.exclude(
            report_task_id__isnull=True).exclude(
            report_task_id__exact='').filter(
            report_task_status__iexact='PENDING'):
        report_task_id = earthquake.report_task_id
        result = AsyncResult(id=report_task_id, app=headless_app)

        # Set the report path if success
        if result.state == 'SUCCESS':
            task_state = 'FAILURE'
            try:
                # Create earthquake report object
                # Set the language manually first
                earthquake_report = EarthquakeReport(
                    earthquake=earthquake, language='en')

                report_path = result.result[
                    'output']['pdf_product_tag']['realtime-earthquake-en']
                with open(report_path, 'rb') as report_file:
                    earthquake_report.report_pdf.save(
                        earthquake_report.report_map_filename,
                        File(report_file),
                        save=True)
                    earthquake.refresh_from_db()
            except BaseException as e:
                LOGGER.exception(e)

            earthquake.report_task_status = task_state
            earthquake.save()
        elif result.state == 'FAILURE':
            Earthquake.objects.filter(id=earthquake.id).update(
                analysis_task_id=result.state)


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
    async_result = run_multi_exposure_analysis.delay(
        hazard_layer_uri,
        EARTHQUAKE_EXPOSURES,
        EARTHQUAKE_AGGREGATION,
    )
    Earthquake.objects.filter(id=event.id).update(
        analysis_task_id=async_result.task_id,
        analysis_task_status=async_result.state)


def generate_earthquake_report(event):
    """Generate report for event.

    :param event: event instance
    :type event: Earthquake
    """
    event.refresh_from_db()
    impact_layer_uri = event.impact_file_path

    result = AsyncResult(id=event.analysis_task_id, app=headless_app)

    layer_order = []

    for layer in EARTHQUAKE_LAYER_ORDER:
        if layer.startswith('@'):
            # substitute layer
            keys = layer[1:].split('.')
            try:
                # Recursively find indexed keys' value
                value = result.result['output']
                for k in keys:
                    value = value[k]
                # substitute if we find replacement
                layer = value
            except BaseException as e:
                LOGGER.exception(e)
                # Let layer order contains @ sign so it can be parsed
                # by InaSAFE Headless instead (and decide if it will fail).

        layer_order.append(layer)

    async_result = generate_report.delay(
        impact_layer_uri, EARTHQUAKE_REPORT_TEMPLATE, layer_order)
    Earthquake.objects.filter(id=event.id).update(
        report_task_id=async_result.task_id,
        report_task_status=async_result.state)
