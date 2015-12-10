# coding=utf-8
import logging
import os
import shutil
import tempfile
from zipfile import ZipFile

from celery import task
from django.conf import settings
from django.contrib.gis.gdal.datasource import DataSource
from django.contrib.gis.geos.collections import MultiPolygon
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.contrib.gis.geos.polygon import Polygon

from realtime.app_settings import LOGGER_NAME
from realtime.models.flood import FloodEventBoundary, Boundary

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/3/15'


LOGGER = logging.getLogger(LOGGER_NAME)


@task()
def process_hazard_layer(flood):
    """Process zipped impact layer and import it to databse

    :param flood: Event id of flood
    :type flood: realtime.models.flood.Flood
    """
    LOGGER.info('Processing impact layer %s - %s' % (
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

        layer_filename = os.path.join(tmpdir, 'flood_data.shp')

        source = DataSource(layer_filename)

        layer = source[0]

        for feat in layer:
            pkey = feat.get('pkey')
            level_name = feat.get('level_name')
            # flooded = feat.get('flooded')
            count = feat.get('count')
            geometry = feat.geom

            geos_geometry = GEOSGeometry(geometry.geojson)

            if isinstance(geos_geometry, Polygon):
                # convert to multi polygon
                geos_geometry = MultiPolygon(geos_geometry)

            try:
                boundary = Boundary.objects.get(upstream_id=pkey)
            except Boundary.DoesNotExist:
                boundary = Boundary.objects.create(
                    upstream_id=pkey,
                    geometry=geos_geometry,
                    name=level_name)
                boundary.save()

            try:
                flooded_boundary = FloodEventBoundary.objects.get(
                    flood=flood,
                    boundary=boundary)
                flooded_boundary.impact_data = int(count)
                flooded_boundary.save()
            except FloodEventBoundary.DoesNotExist:
                flooded_boundary = FloodEventBoundary.objects.create(
                    flood=flood,
                    boundary=boundary,
                    impact_data=int(count))

        shutil.rmtree(tmpdir)

    LOGGER.info('Hazard layer processed...')
    # read shp
