# coding=utf-8
from __future__ import absolute_import

import json
import logging
import os

from celery import chain
from celery.result import AsyncResult

from django.core.files import File
from realtime.utils import substitute_layer_order

from realtime.app_settings import (
    OSM_LEVEL_7_NAME,
    OSM_LEVEL_8_NAME,
    FLOOD_EXPOSURE,
    FLOOD_AGGREGATION,
    FLOOD_LAYER_ORDER,
    FLOOD_REPORT_TEMPLATE,
)
from core.celery_app import app
from django.contrib.gis.gdal.datasource import DataSource
from django.contrib.gis.geos.collections import MultiPolygon
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.contrib.gis.geos.polygon import Polygon
from django.db.models import Sum

from realtime.app_settings import LOGGER_NAME
from realtime.models.flood import (
    Flood,
    FloodEventBoundary,
    FloodReport,
    Boundary,
    BoundaryAlias,
    ImpactEventBoundary)
from realtime.tasks.realtime.flood import process_flood
from realtime.tasks.headless.inasafe_wrapper import (
    run_analysis, generate_report, RESULT_SUCCESS)
from realtime.tasks.headless.celery_app import app as headless_app

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/3/15'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(queue='inasafe-django')
def check_processing_task():
    """Checking flood processing task."""
    # Checking analysis task
    # for flood in Flood.objects.exclude(
    #         analysis_task_id__isnull=True).exclude(
    #         analysis_task_id__exact='').filter(
    #         analysis_task_status__iexact='PENDING'):
    #     analysis_task_id = flood.analysis_task_id
    #     result = AsyncResult(id=analysis_task_id, app=headless_app)
    #     analysis_result = result.result
    #
    #     if result.state == 'SUCCESS':
    #         task_state = 'FAILURE'
    #         try:
    #             flood.impact_file_path = result.result['output'][
    #                 'analysis_summary']
    #             task_state = 'SUCCESS'
    #         except BaseException as e:
    #             LOGGER.exception(e)
    #         flood.analysis_task_status = task_state
    #         flood.analysis_task_result = json.dumps(analysis_result)
    #         flood.save()
    #         process_impact_layer.delay(flood)
    # Checking report generation task
    # for flood in Flood.objects.exclude(
    #         report_task_id__isnull=True).exclude(
    #         report_task_id__exact='').filter(
    #         report_task_status__iexact='PENDING'):
    #     report_task_id = flood.report_task_id
    #     result = AsyncResult(id=report_task_id, app=headless_app)
    #     analysis_result = result.result
    #     if result.state == 'SUCCESS':
    #         task_state = 'FAILURE'
    #         try:
    #             report_path = result.result[
    #                 'output']['pdf_product_tag']['realtime-flood-en']
    #             # Create flood report object
    #             # Set the language manually first
    #             flood_report = FloodReport(flood=flood, language='en')
    #             with open(report_path, 'rb') as report_file:
    #                 flood_report.impact_map.save(
    #                     flood_report.impact_map_filename,
    #                     File(report_file),
    #                     save=True)
    #             task_state = 'SUCCESS'
    #         except BaseException as e:
    #             LOGGER.exception(e)
    #
    #         flood.report_task_status = task_state
    #         flood.report_task_result = json.dumps(analysis_result)
    #         flood.save()


@app.task(queue='inasafe-django')
def process_hazard_layer(flood):
    """Process hazard layer and import it to database

    :param flood: Event id of flood
    :type flood: realtime.models.flood.Flood
    """
    LOGGER.info('Processing hazard layer %s' % flood.event_id)
    # extract hazard layer zip file
    if not os.path.exists(flood.hazard_path):
        LOGGER.info('No hazard layer at %s' % flood.hazard_path)
        return

    # process hazard layer
    layer_filename = flood.hazard_path

    source = DataSource(layer_filename)

    layer = source[0]

    FloodEventBoundary.objects.filter(flood=flood).delete()

    kelurahan = BoundaryAlias.objects.get(alias=OSM_LEVEL_7_NAME)
    rw = BoundaryAlias.objects.get(alias=OSM_LEVEL_8_NAME)

    for feat in layer:
        if not flood.data_source or flood.data_source == 'petajakarta':
            upstream_id = feat.get('pkey')
            level_name = feat.get('level_name')
            parent_name = feat.get('parent_nam')
            state = feat.get('state')
        elif flood.data_source == 'petabencana':
            upstream_id = feat.get('area_id')
            level_name = feat.get('area_name')
            parent_name = feat.get('parent_name')
            state = feat.get('state')
        elif flood.data_source == 'Hazard File':
            upstream_id = feat.get('area_id')
            level_name = feat.get('area_name')
            parent_name = feat.get('parent_name')
            state = feat.get('state')

        geometry = feat.geom

        geos_geometry = GEOSGeometry(geometry.geojson)

        if isinstance(geos_geometry, Polygon):
            # convert to multi polygon
            geos_geometry = MultiPolygon(geos_geometry)

        # check parent exists
        try:
            boundary_kelurahan = Boundary.objects.get(
                name__iexact=parent_name.strip(),
                boundary_alias=kelurahan)
        except Boundary.DoesNotExist:
            boundary_kelurahan = Boundary.objects.create(
                upstream_id=upstream_id,
                geometry=geos_geometry,
                name=parent_name,
                boundary_alias=kelurahan)
            boundary_kelurahan.save()

        try:
            boundary_rw = Boundary.objects.get(
                upstream_id=upstream_id, boundary_alias=rw)
            boundary_rw.geometry = geos_geometry
            boundary_rw.name = level_name
            boundary_rw.parent = boundary_kelurahan
        except Boundary.DoesNotExist:
            boundary_rw = Boundary.objects.create(
                upstream_id=upstream_id,
                geometry=geos_geometry,
                name=level_name,
                parent=boundary_kelurahan,
                boundary_alias=rw)

        boundary_rw.save()

        if not state or int(state) == 0:
            continue

        FloodEventBoundary.objects.create(
            flood=flood,
            boundary=boundary_rw,
            hazard_data=int(state))

    # Store boundary flooded in flood
    flood.boundary_flooded = calculate_boundary_flooded(flood)
    # prevent infinite recursive save
    flood.save(update_fields=['boundary_flooded'])

    LOGGER.info('Hazard layer processed...')
    return True


@app.task(queue='inasafe-django')
def process_impact_layer(flood):
    """Process zipped impact layer and import it to databse

    :param flood: Event id of flood
    :type flood: realtime.models.flood.Flood
    """
    LOGGER.info('Processing impact layer %s ' % flood.event_id)

    # Get impact analysis file path
    analysis_directory = os.path.dirname(flood.impact_file_path)
    impact_analysis_path = os.path.join(
        analysis_directory, 'impact_analysis.geojson')

    if not os.path.exists(impact_analysis_path):
        LOGGER.info('No impact analysis layer')
        return

    source = DataSource(impact_analysis_path)

    layer = source[0]

    ImpactEventBoundary.objects.filter(flood=flood).delete()

    kelurahan = BoundaryAlias.objects.get(alias=OSM_LEVEL_7_NAME)

    for feat in layer:
        affected = feat.get('affected')
        if affected != 'True':
            continue

        hazard_class = feat.get('hazard_class')
        level_7_name = feat.get('exposure_name').strip()
        population_affected = feat.get('population')
        geometry = feat.geom
        geos_geometry = GEOSGeometry(geometry.geojson)

        if isinstance(geos_geometry, Polygon):
            # convert to multi polygon
            geos_geometry = MultiPolygon(geos_geometry)

        try:
            boundary_kelurahan = Boundary.objects.get(
                name__iexact=level_7_name,
                boundary_alias=kelurahan)
        except Boundary.DoesNotExist:
            LOGGER.debug('Boundary does not exists: %s' % level_7_name)
            LOGGER.debug('Kelurahan Boundary should have been filled '
                         'already')
            # Will try to create new one
            boundary_kelurahan = Boundary.objects.create(
                geometry=geos_geometry,
                name=level_7_name,
                boundary_alias=kelurahan)
            boundary_kelurahan.save()

        ImpactEventBoundary.objects.create(
            flood=flood,
            parent_boundary=boundary_kelurahan,
            geometry=geos_geometry,
            affected=affected,
            population_affected=population_affected,
            hazard_class=hazard_class
        )
    # Store affected population in flood
    flood.total_affected = calculate_affected_population(flood)
    # prevent infinite recursive save
    flood.save(update_fields=['total_affected'])

    LOGGER.info('Impact layer processed...')
    return True


def calculate_boundary_flooded(flood):
    """Calculate the number of boundary flooded for a flood in RW level.

    :param flood: The flood.
    :type flood: Flood

    :returns: The number of flooded boundary.
    :rtype: int
    """
    rw = BoundaryAlias.objects.get(alias=OSM_LEVEL_8_NAME)
    boundary_flooded = FloodEventBoundary.objects.filter(
        flood=flood,
        boundary__boundary_alias=rw).count()
    return boundary_flooded or 0


def calculate_affected_population(flood):
    """Calculate the number of affected population for in kelurahan level.

    :param flood: The flood.
    :type flood: Flood

    :returns: The number of affected population.
    :rtype: int
    """
    kelurahan = BoundaryAlias.objects.get(alias=OSM_LEVEL_7_NAME)
    total_population_affected = ImpactEventBoundary.objects.filter(
        flood=flood,
        parent_boundary__boundary_alias=kelurahan
    ).aggregate(
        total_population_affected=Sum('population_affected'))
    try:
        total_affected = total_population_affected[
            'total_population_affected'] or 0
    except KeyError:
        total_affected = 0

    return total_affected


@app.task(queue='inasafe-django')
def recalculate_impact_info(flood):
    """Recalculate flood impact data.

    :param flood: Flood object
    :type flood: realtime.models.flood.Flood
    """
    # calculate total boundary flooded in RW level
    flood.boundary_flooded = calculate_boundary_flooded(flood)

    # calculate total population affected in kelurahan level
    flood.total_affected = calculate_affected_population(flood)

    # prevent infinite recursive save
    flood.save(update_fields=['total_affected', 'boundary_flooded'])


@app.task(queue='inasafe-django')
def create_flood_report():
    process_flood.delay()
    LOGGER.info('Processing flood...')


@app.task(queue='inasafe-django')
def generate_event_report(flood_event):
    """Generate Flood report

    :param flood_event: Flood event instance
    :type flood_event: Flood
    :return:
    """
    if not flood_event.flood_data:
        with open(flood_event.hazard_path) as f:
            flood_data = f.read()

        Flood.objects.filter(
            id=flood_event.id).update(
            flood_data=flood_data
        )

    if (flood_event.hazard_layer_exists and
            not flood_event.impact_layer_exists and
            flood_event.need_run_analysis):

        run_flood_analysis(flood_event)

    elif (flood_event.hazard_layer_exists and
            flood_event.impact_layer_exists and
            not flood_event.has_reports and
            flood_event.need_generate_reports):

        generate_flood_report(flood_event)


def run_flood_analysis(flood_event):
    """Run flood analysis.

    :param flood_event: Flood event instance
    :type flood_event: Flood
    """
    flood_event.refresh_from_db()

    hazard_layer_uri = flood_event.hazard_path

    tasks_chain = chain(
        # Run analysis
        run_analysis.s(
            hazard_layer_uri,
            FLOOD_EXPOSURE,
            FLOOD_AGGREGATION,
        ).set(queue=run_analysis.queue),

        # Handle analysis product
        handle_analysis.s(
            flood_event.id
        ).set(queue=handle_analysis.queue)
    )

    @app.task
    def _handle_error(req, exc, traceback):
        """Update task status as Failure."""
        Flood.objects.filter(id=flood_event.id).update(
            analysis_task_status='FAILURE')

    async_result = tasks_chain.apply_async(link_error=_handle_error.s())
    Flood.objects.filter(id=flood_event.id).update(
        analysis_task_id=async_result.task_id,
        analysis_task_status=async_result.state)


@app.task(queue='inasafe-django')
def handle_analysis(analysis_result, event_id):
    """Handle analysis products"""
    flood = Flood.objects.get(id=event_id)

    task_state = 'FAILURE'
    if analysis_result['status'] == RESULT_SUCCESS:
        try:
            flood.impact_file_path = analysis_result['output'][
                'analysis_summary']

            flood.save(update_fields=['impact_file_path'])

            # Flood.objects.get(id=flood.id).update(
            #     impact_file_path=impact_file_path)

            task_state = 'SUCCESS'
            process_impact_layer(flood)
        except BaseException as e:
            LOGGER.exception(e)
    else:
        LOGGER.error(analysis_result['message'])

    flood.analysis_task_status = task_state
    flood.analysis_task_result = json.dumps(analysis_result)


def generate_flood_report(flood_event):
    """Generate ash report for flood event.

    :param flood_event: Flood event instance
    :type flood_event: Flood
    """
    flood_event.refresh_from_db()

    impact_layer_uri = flood_event.impact_file_path

    analysis_result = json.loads(flood_event.analysis_task_result)

    source_dict = dict(analysis_result['output'])
    source_dict.update({
        'hazard': flood_event.hazard_path
    })

    layer_order = substitute_layer_order(
        FLOOD_LAYER_ORDER, source_dict)

    tasks_chain = chain(
        # Generate report
        generate_report.s(
            impact_layer_uri, FLOOD_REPORT_TEMPLATE, layer_order
        ).set(queue=generate_report.queue),

        # Handle report
        handle_report.s(
            flood_event.id
        ).set(queue=handle_report.queue)
    )

    @app.task
    def _handle_error(req, exc, traceback):
        """Update task status as Failure."""
        Flood.objects.filter(id=flood_event.id).update(
            report_task_status='FAILURE')

    async_result = tasks_chain.apply_async(link_error=_handle_error.s())

    Flood.objects.filter(id=flood_event.id).update(
        report_task_id=async_result.task_id,
        report_task_status=async_result.state)


@app.task(queue='inasafe-django')
def handle_report(report_result, event_id):
    """Handle report product"""
    flood = Flood.objects.get(id=event_id)

    # Set the report path if success
    task_state = 'FAILURE'
    if report_result['status'] == RESULT_SUCCESS:
        try:
            # Create report object
            # Set the language manually first
            report = FloodReport(
                flood=flood, language='en')

            report_path = report_result[
                'output']['pdf_product_tag']['realtime-flood-en']
            with open(report_path, 'rb') as report_file:
                report.impact_map.save(
                    report.impact_map_filename,
                    File(report_file),
                    save=True)
                flood.refresh_from_db()
            task_state = 'SUCCESS'
        except BaseException as e:
            LOGGER.exception(e)
    else:
        LOGGER.error(report_result['message'])

    Flood.objects.filter(id=flood.id).update(
        report_task_status=task_state,
        report_task_result=json.dumps(report_result))
