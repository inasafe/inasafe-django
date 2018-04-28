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
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, Polygon, MultiPolygon
from django.core.files import File
from django.core.urlresolvers import reverse

from core.celery_app import app
from realtime.app_settings import LOGGER_NAME, FELT_EARTHQUAKE_URL, \
    EARTHQUAKE_EXPOSURES, EARTHQUAKE_AGGREGATION, \
    EARTHQUAKE_LAYER_ORDER, GRID_FILE_DEFAULT_NAME, \
    EARTHQUAKE_REPORT_TEMPLATE_EN
from realtime.helpers.inaware import InAWARERest
from realtime.models.earthquake import Earthquake, EarthquakeMMIContour
from realtime.tasks.headless.inasafe_wrapper import \
    run_multi_exposure_analysis, generate_report, RESULT_SUCCESS
from realtime.utils import substitute_layer_order

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
def generate_event_report(earthquake_event, locale='en'):
    """Generate Earthquake report

    :param earthquake_event: Earthquake event instance
    :type earthquake_event: Earthquake
    :return:
    """
    earthquake_event.inspected_language = locale
    if not earthquake_event.hazard_layer_exists:

        # Skip all process if not exists
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

        # Do not use save, to avoid triggering signals
        Earthquake.objects.filter(
            id=earthquake_event.id).update(
            shake_grid_xml=shake_grid_xml)

        earthquake_event.refresh_from_db()

        # Remove un-needed Grid XML
        if earthquake_event.shake_grid:
            earthquake_event.shake_grid.delete(save=False)

        # Find matching initial shakemaps if this is a corrected one
        initial_event = earthquake_event.initial_shakemaps
        if initial_event:
            initial_event.mark_shakemaps_has_corrected()

        # Find matching corrected shakemaps if this is an initial one
        corrected_event = earthquake_event.corrected_shakemaps
        if corrected_event:
            # Set into property because it will gets saved.
            earthquake_event.has_corrected = True

        # Use save to trigger signals again
        earthquake_event.save()

    # Check impact layer
    elif (not earthquake_event.impact_layer_exists and
            earthquake_event.need_run_analysis):

        # If hazard exists but impact layer is not, then create a new analysis
        # job.
        run_earthquake_analysis(earthquake_event, locale=locale)

    # Check MMI Contour saved
    elif (earthquake_event.mmi_layer_exists and
            EarthquakeMMIContour.objects.filter(
                earthquake=earthquake_event).count() == 0):
        # Don't use celery for this
        process_mmi_layer(earthquake_event)
        earthquake_event.save()

    # Check report
    elif (not earthquake_event.has_reports and
            earthquake_event.need_generate_reports):

        # If analysis is done but report doesn't exists, then create the
        # reports.
        generate_earthquake_report(earthquake_event, locale=locale)


def run_earthquake_analysis(event, locale='en'):
    """Run analysis.

    :param event: event instance
    :type event: Earthquake
    """
    event = Earthquake.objects.get(id=event.id)
    event.inspected_language = locale
    hazard_layer_uri = event.hazard_path

    tasks_chain = chain(
        # Run multi exposure analysis
        run_multi_exposure_analysis.s(
            hazard_layer_uri,
            EARTHQUAKE_EXPOSURES,
            EARTHQUAKE_AGGREGATION,
            locale=locale
        ).set(queue=run_multi_exposure_analysis.queue),

        # Handle analysis products
        handle_analysis.s(
            event.id,
            locale=locale
        ).set(queue=handle_analysis.queue),
    )

    @app.task
    def _handle_error(req, exc, traceback):
        """Update task status as Failure."""
        impact_object = event.impact_object
        impact_object.analysis_task_status = 'Failure'
        impact_object.save()

    async_result = tasks_chain.apply_async(link_error=_handle_error.s())
    impact_object = event.impact_object
    impact_object.analysis_task_id = async_result.task_id
    impact_object.analysis_task_status = async_result.state
    impact_object.save()


@app.task(queue='inasafe-django')
def process_mmi_layer(earthquake):
    """Process MMI contour layer and import it to database

    :param earthquake: Instance of Earthquake
    :type earthquake: realtime.models.earthquake.Earthquake
    """
    LOGGER.info('Processing MMI contour {0}'.format(
        earthquake.event_id_formatted))

    if not earthquake.mmi_layer_exists:
        LOGGER.info('No MMI Contour layer at {0}'.format(
            earthquake.mmi_output_path))
        return

    layer_filename = earthquake.mmi_output_path

    source = DataSource(layer_filename)

    layer = source[0]

    EarthquakeMMIContour.objects.filter(earthquake=earthquake).delete()

    for feat in layer:
        if 'MMI' in feat.fields:
            mmi = feat.get('MMI')
        elif 'mmi' in feat.fields:
            mmi = feat.get('mmi')
        else:
            mmi = 0

        properties = {}
        for field in feat.fields:
            properties[field] = feat.get(field)

        geometry = feat.geom

        geos_geometry = GEOSGeometry(geometry.geojson)

        if isinstance(geos_geometry, Polygon):
            # convert to multi polygon
            geos_geometry = MultiPolygon(geos_geometry)

        EarthquakeMMIContour.objects.create(
            earthquake=earthquake,
            geometry=geos_geometry,
            mmi=mmi,
            properties=json.dumps(properties))

    earthquake.refresh_from_db()
    earthquake.mark_shakemaps_has_contours()

    LOGGER.info('MMI Contour processed...')
    return True


@app.task(queue='inasafe-django')
def handle_analysis(analysis_result, event_id, locale='en'):
    """Handle analysis products"""
    earthquake = Earthquake.objects.get(id=event_id)
    earthquake.inspected_language = locale

    task_state = 'FAILURE'
    if analysis_result['status'] == RESULT_SUCCESS:
        try:
            earthquake.impact_file_path = analysis_result[
                'output']['analysis_summary']
            earthquake.mmi_output_path = analysis_result[
                'output']['population']['earthquake_contour']

            # save earthquake MMI Contour
            process_mmi_layer.delay(earthquake)
            task_state = 'SUCCESS'
        except BaseException as e:
            LOGGER.exception(e)
    else:
        LOGGER.error(analysis_result['message'])

    earthquake.analysis_task_status = task_state
    earthquake.analysis_task_result = json.dumps(analysis_result)
    earthquake.save()

    return analysis_result


def generate_earthquake_report(event, locale='en'):
    """Generate report for event.

    :param event: event instance
    :type event: Earthquake
    """
    event = Earthquake.objects.get(id=event.id)
    event.inspected_language = locale
    impact_layer_uri = event.impact_file_path

    # do nothing if task result was not ready
    if not event.analysis_task_result:
        return

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
            impact_layer_uri, EARTHQUAKE_REPORT_TEMPLATE_EN, layer_order,
            locale=locale
        ).set(queue=generate_report.queue),

        # Handle report
        handle_report.s(
            event.id,
            locale=locale
        ).set(queue=handle_report.queue)
    )

    @app.task
    def _handle_error(req, exc, traceback):
        """Update task status as Failure."""
        # Earthquake.objects.filter(id=event.id).update(
        #     report_task_status='FAILURE')
        report_object = event.report_object
        report_object.report_task_status = 'FAILURE'
        report_object.save()

    async_result = tasks_chain.apply_async(link_error=_handle_error.s())

    # Earthquake.objects.filter(id=event.id).update(
    #     report_task_id=async_result.task_id,
    #     report_task_status=async_result.state)
    report_object = event.report_object
    report_object.report_task_id = async_result.task_id
    report_object.report_task_status = async_result.state
    report_object.save()


@app.task(queue='inasafe-django')
def handle_report(report_result, event_id, locale='en'):
    """Handle report product"""
    earthquake = Earthquake.objects.get(id=event_id)
    earthquake.inspected_language = locale
    report_object = earthquake.report_object

    # Set the report path if success
    task_state = 'FAILURE'
    if report_result['status'] == RESULT_SUCCESS:
        try:

            report_path = report_result[
                'output']['pdf_product_tag']['realtime-earthquake-en']
            with open(report_path, 'rb') as report_file:
                report_object.report_pdf.save(
                    report_object.report_map_filename,
                    File(report_file),
                    save=True)
                earthquake.refresh_from_db()
            task_state = 'SUCCESS'
        except BaseException as e:
            LOGGER.exception(e)
    else:
        LOGGER.error(report_result['message'])

    # Earthquake.objects.filter(id=earthquake.id).update(
    #     report_task_status=task_state,
    #     report_task_result=json.dumps(report_result))
    report_object.report_task_status = task_state
    report_object.report_task_result = json.dumps(report_result)
    report_object.save()

    return report_result
