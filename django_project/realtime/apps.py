# coding=utf-8
import logging

from django.apps import AppConfig
from realtime.app_settings import LOGGER_NAME

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '4/1/16'


OSM_LEVEL_7_NAME = 'Kelurahan'
OSM_LEVEL_8_NAME = 'RW'


LOGGER = logging.getLogger(LOGGER_NAME)


class RealtimeConfig(AppConfig):
    name = 'realtime'
    verbose_name = 'Realtime Application'

    def ready(self):
        # check default boundary alias exists

        try:
            BoundaryAlias = self.get_model('BoundaryAlias')
            try:
                kelurahan = BoundaryAlias.objects.get(alias=OSM_LEVEL_7_NAME)
            except BoundaryAlias.DoesNotExist:
                kelurahan = BoundaryAlias.objects.create(
                    alias=OSM_LEVEL_7_NAME,
                    osm_level=7)
            try:
                rw = BoundaryAlias.objects.get(alias=OSM_LEVEL_8_NAME)
            except BoundaryAlias.DoesNotExist:
                rw = BoundaryAlias.objects.create(
                    alias=OSM_LEVEL_8_NAME,
                    osm_level=8,
                    parent=kelurahan)
        except Exception as e:
            LOGGER.error(e)

