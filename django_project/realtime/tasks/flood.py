# coding=utf-8
from __future__ import absolute_import

import logging
import os
import shutil
import tempfile
from zipfile import ZipFile

from django.contrib.gis.gdal.error import OGRIndexError

from realtime.app_settings import (
    OSM_LEVEL_7_NAME,
    OSM_LEVEL_8_NAME,
    FLOOD_EXPOSURE,
    FLOOD_AGGREGATION,
    FLOOD_LAYER_ORDER,
    FLOOD_REPORT_TEMPLATE,
)
from core.celery_app import app
from django.conf import settings
from django.contrib.gis.gdal.datasource import DataSource
from django.contrib.gis.geos.collections import MultiPolygon
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.contrib.gis.geos.polygon import Polygon
from django.db.models import Sum

from realtime.app_settings import LOGGER_NAME
from realtime.models.flood import (
    Flood,
    FloodEventBoundary,
    Boundary,
    BoundaryAlias,
    ImpactEventBoundary)
from realtime.tasks.realtime.flood import process_flood
from realtime.tasks.headless.inasafe_wrapper import (
    run_analysis, generate_report)

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/3/15'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(queue='inasafe-django')
def process_hazard_layer(flood):
    """Process zipped impact layer and import it to databse

    :param flood: Event id of flood
    :type flood: realtime.models.flood.Flood
    """
    LOGGER.info('Processing hazard layer %s - %s' % (
        flood.event_id,
        flood.hazard_layer.name
    ))
    # extract hazard layer zip file
    if not flood.hazard_layer or not flood.hazard_layer.name:
        LOGGER.info('No hazard layer')
        return
    zip_file_path = os.path.join(settings.MEDIA_ROOT, flood.hazard_layer.name)

    if not os.path.exists(zip_file_path):
        LOGGER.info('Hazard layer doesn\'t exists')
        return

    with ZipFile(zip_file_path) as zf:
        tmpdir = tempfile.mkdtemp()

        zf.extractall(path=tmpdir)

        # process hazard layer
        layer_filename = os.path.join(tmpdir, 'flood_data.shp')

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
                parent_name = feat.get('parent_nam')
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

        shutil.rmtree(tmpdir)

    LOGGER.info('Hazard layer processed...')
    return True


@app.task(queue='inasafe-django')
def process_impact_layer(flood):
    """Process zipped impact layer and import it to databse

    :param flood: Event id of flood
    :type flood: realtime.models.flood.Flood
    """
    LOGGER.info('Processing impact layer %s - %s' % (
        flood.event_id,
        flood.impact_layer.name
    ))
    # extract hazard layer zip file
    if not flood.impact_layer or not flood.impact_layer.name:
        LOGGER.info('No impact layer')
        return

    zip_file_path = os.path.join(settings.MEDIA_ROOT,
                                 flood.impact_layer.name)

    if not os.path.exists(zip_file_path):
        LOGGER.info('Impact layer doesn\'t exists')
        return

    with ZipFile(zip_file_path) as zf:
        # Now process population impacted layer
        tmpdir = tempfile.mkdtemp()

        zf.extractall(path=tmpdir)

        layer_filename = os.path.join(tmpdir, 'impact.shp')

        source = DataSource(layer_filename)

        layer = source[0]

        ImpactEventBoundary.objects.filter(flood=flood).delete()

        kelurahan = BoundaryAlias.objects.get(alias=OSM_LEVEL_7_NAME)

        for feat in layer:
            level_7_name = feat.get('NAMA_KELUR').strip()
            try:
                hazard_class = feat.get('affected')
            except OGRIndexError:
                hazard_class = feat.get('safe_ag')
            population_affected = feat.get('Pop_Total')
            geometry = feat.geom
            geos_geometry = GEOSGeometry(geometry.geojson)

            if isinstance(geos_geometry, Polygon):
                # convert to multi polygon
                geos_geometry = MultiPolygon(geos_geometry)

            if hazard_class <= 1:
                continue

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
                hazard_class=hazard_class,
                population_affected=population_affected)

        shutil.rmtree(tmpdir)
    LOGGER.info('Impact layer processed...')
    return True


@app.task(queue='inasafe-django')
def recalculate_impact_info(flood):
    """Recalculate flood impact data.

    :param flood: Flood object
    :type flood: realtime.models.flood.Flood
    """
    # calculate total boundary flooded in RW level
    rw = BoundaryAlias.objects.get(alias=OSM_LEVEL_8_NAME)
    boundary_flooded = FloodEventBoundary.objects.filter(
        flood=flood,
        boundary__boundary_alias=rw).count()
    flood.boundary_flooded = boundary_flooded or 0

    # calculate total population affected in kelurahan level
    kelurahan = BoundaryAlias.objects.get(alias=OSM_LEVEL_7_NAME)
    total_population_affected = ImpactEventBoundary.objects.filter(
        flood=flood,
        parent_boundary__boundary_alias=kelurahan
    ).aggregate(
        total_population_affected=Sum('population_affected'))
    try:
        flood.total_affected = total_population_affected[
            'total_population_affected'] or 0
    except KeyError:
        flood.total_affected = 0
        pass

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
    async_result = run_analysis.delay(
        flood_event.hazard_path,
        FLOOD_EXPOSURE,
        FLOOD_AGGREGATION
    )
    Flood.objects.filter(id=flood_event.id).update(
        analysis_task_id=async_result.task_id,
        analysis_task_status=async_result.state)


def generate_flood_report(flood_event):
    """Generate ash report for flood event.

    :param flood_event: Flood event instance
    :type flood_event: Flood
    """
    layer_order = list(FLOOD_LAYER_ORDER)
    if 'flood_layer_path' in layer_order:
        hazard_index = layer_order.index('flood_layer_path')
        layer_order[hazard_index] = flood_event.hazard_path
    async_result = generate_report.delay(
        flood_event.impact_file_path, FLOOD_REPORT_TEMPLATE, layer_order)
    Flood.objects.filter(id=flood_event.id).update(
        report_task_id=async_result.task_id,
        report_task_status=async_result.state)
