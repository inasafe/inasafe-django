# coding=utf-8
import logging

import os
from django.contrib.gis.gdal.datasource import DataSource
from django.contrib.gis.geos.collections import MultiPolygon
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.contrib.gis.geos.polygon import Polygon
from django.core.management.base import BaseCommand
from django.db.models.query_utils import Q

from realtime.app_settings import LOGGER_NAME

from realtime.models.flood import BoundaryAlias, Boundary

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '5/18/16'


LOGGER = logging.getLogger(LOGGER_NAME)


class Command(BaseCommand):
    """Script to import OSM Boundary data to the database

    """
    args = '[layer_path] [parent_field] [name_field] [osm_level] ' \
           '[osm_level_alias]'
    help = 'Command to import boundary data from shp layer'

    # noqa: max-complexity=20
    def handle(self, *args, **options):
        print args
        try:
            if len(args) != 5:
                return
            layer_path = args[0]
            if not os.path.exists(layer_path):
                print '%s does not exists' % layer_path
                return
            parent_field = args[1]
            name_field = args[2]
            osm_level = int(args[3])
            osm_level_alias = args[4]
            source = DataSource(layer_path)
            layer = source[0]
        except Exception as e:
            raise e

        try:
            boundary_alias = BoundaryAlias.objects.get(
                alias__iexact=osm_level_alias,
                osm_level=osm_level)
        except BoundaryAlias.DoesNotExist:
            boundary_alias = BoundaryAlias.objects.create(
                alias=osm_level_alias,
                osm_level=osm_level)

        new_boundary = 0
        existing_boundary = 0

        for feat in layer:
            geometry = feat.geom
            name = feat.get(name_field)
            parent_name = None
            if parent_field:
                parent_name = feat.get(parent_field)

            geos_geometry = GEOSGeometry(geometry.geojson)

            # check parent boundary exists
            parent_boundary = None
            try:
                if parent_name:
                    parent_boundary = Boundary.objects.get(
                        name__iexact=parent_name.strip(),
                        boundary_alias__osm_level=osm_level - 1)
            except Boundary.DoesNotExist:
                pass

            if isinstance(geos_geometry, Polygon):
                geos_geometry = MultiPolygon(geos_geometry)

            try:
                query = (
                    Q(name__iexact=name.strip()) &
                    Q(boundary_alias=boundary_alias))
                if parent_boundary:
                    query = query & Q(parent=parent_boundary)
                boundary = Boundary.objects.get(query)
                if boundary:
                    existing_boundary += 1
            except Boundary.DoesNotExist:
                Boundary.objects.create(
                    name=name.strip(),
                    parent=parent_boundary,
                    geometry=geos_geometry,
                    boundary_alias=boundary_alias)
                new_boundary += 1

        print 'New Boundary %s' % new_boundary
        print 'Existing Boundary %s' % existing_boundary
        LOGGER.info('Shapefile processed...')
