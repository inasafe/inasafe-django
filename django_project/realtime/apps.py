# coding=utf-8
import logging

from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.gis.geos.point import Point

from user_map.models.user import User

from realtime.app_settings import LOGGER_NAME, REST_GROUP

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
                BoundaryAlias.objects.get(alias=OSM_LEVEL_8_NAME)
            except BoundaryAlias.DoesNotExist:
                BoundaryAlias.objects.create(
                    alias=OSM_LEVEL_8_NAME,
                    osm_level=8,
                    parent=kelurahan)
        except Exception as e:
            LOGGER.error(e)

        # check test user exists:
        if settings.DEV_MODE:
            # User = self.get_model('user_map.models.user.User')
            try:
                test_user = User.objects.get(
                    email='test@realtime.inasafe.org')
            except User.DoesNotExist:
                location = Point(106.8222713, -6.1856145)
                realtime_group = Group.objects.get(name=REST_GROUP)

                test_user = User.objects.create_user(
                    email='test@realtime.inasafe.org',
                    username='test user',
                    location=location,
                    password='t3st4ccount',
                    email_updates=False)
                test_user.groups.add(realtime_group)
                test_user.is_superuser = True
                test_user.is_admin = True
                test_user.save()
