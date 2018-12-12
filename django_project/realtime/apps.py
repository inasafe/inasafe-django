# coding=utf-8

import logging

from django.apps import AppConfig, apps
from django.conf import settings
from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Group
from django.contrib.contenttypes.management import update_contenttypes
from django.contrib.gis.geos.point import Point

from realtime.app_settings import LOGGER_NAME, REST_GROUP, OSM_LEVEL_7_NAME, \
    OSM_LEVEL_8_NAME, VOLCANO_GROUP, ASH_GROUP, VOLCANO_LAYER_PATH
from realtime.models.volcano import load_volcano_data
from user_map.models.user import User

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '4/1/16'


LOGGER = logging.getLogger(LOGGER_NAME)


class RealtimeConfig(AppConfig):
    name = 'realtime'
    verbose_name = 'Realtime Application'

    def load_boundary_alias(self):
        """check default boundary alias exists"""
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

    def load_volcano_fixtures(self):
        """load volcano fixtures samples"""
        try:
            Volcano = self.get_model('Volcano')
            if Volcano.objects.all().count() == 0:
                load_volcano_data(Volcano, VOLCANO_LAYER_PATH)
        except Exception as e:
            LOGGER.error(e)

    def load_test_users(self):
        """Load test users if in DEV MODE"""
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

            try:
                test_user = User.objects.get(
                    email='volcano@realtime.inasafe.org')
            except User.DoesNotExist:
                location = Point(106.8222713, -6.1856145)
                volcano_group = Group.objects.get(name=VOLCANO_GROUP)
                ash_group = Group.objects.get(name=ASH_GROUP)

                test_user = User.objects.create_user(
                    email='volcano@realtime.inasafe.org',
                    username='test ash user',
                    location=location,
                    password='t3st4ccount',
                    email_updates=False)
                test_user.groups.add(volcano_group)
                test_user.groups.add(ash_group)
                test_user.is_superuser = False
                test_user.is_admin = True
                test_user.is_confirmed = True
                test_user.save()

    def create_rest_group(self):
        """Helper file for unittests to generate REST Group."""
        # update content types
        update_contenttypes(self, interactive=False)
        # update permissions
        create_permissions(self, interactive=False)
        Group = apps.get_model('auth', 'Group')
        group_list = [
            (REST_GROUP, [
                'ash',
                'floodreport',
                'earthquakereport',
                'impacteventboundary',
                'flood',
                'userpush',
                'boundary',
                'boundaryalias',
                'floodeventboundary',
                'earthquake',
                'volcano',
                'ashreport'
            ]),
            (VOLCANO_GROUP, [
                'volcano',
            ]),
            (ASH_GROUP, [
                'ash',
                'ashreport',
            ]),
        ]
        for g in group_list:
            try:
                realtime_group = Group.objects.get(name=g[0])
            except Group.DoesNotExist:
                realtime_group = Group.objects.create(name=g[0])

            Permission = apps.get_model('auth', 'Permission')
            for m in g[1]:
                realtime_permissions = Permission.objects.filter(
                    content_type__app_label='realtime',
                    content_type__model=m)

                realtime_group.permissions.add(*realtime_permissions)
                realtime_group.save()

    def ready(self):
        try:
            self.load_boundary_alias()
            self.load_volcano_fixtures()
            self.load_test_users()
        except BaseException as e:
            LOGGER.exception(e)
            pass

        # attach signals
        from realtime import signals  # noqa
