# coding=utf-8
import logging

import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from django.conf import settings
from django.contrib.gis.geos.point import Point
from django.core.files.base import File
from rest_framework.test import APITestCase

from core.settings.utils import ABS_PATH
from realtime.app_settings import LOGGER_NAME, REST_GROUP
from realtime.models.flood import Flood
from realtime.tasks.flood import process_hazard_layer

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/4/15'


LOGGER = logging.getLogger(LOGGER_NAME)


class TestFloodTask(APITestCase):

    def data_path(self, filename):
        return u'realtime/tests/data/flood/'+filename

    def setUp(self):
        if settings.TESTING:
            # move to media root for testing purposes
            self.default_media_path = settings.MEDIA_ROOT
            settings.MEDIA_ROOT = ABS_PATH('media_test')

        Flood.objects.create(
            event_id=u'2015112518-3-rw',
            time=datetime.datetime(
                2015, 11, 25, 18, 0, 0
            ),
            interval=3,
            source=u'Peta Jakarta',
            region=u'Jakarta',
            hazard_layer=File(open(
                self.data_path('hazard.zip')
            ))
        )

        # create test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username='test',
            email='test@test.org',
            password='testsecret',
            location=Point(0, 0),
            email_updates=False)
        realtime_group = Group.objects.get(name=REST_GROUP)
        self.user.groups.add(realtime_group)
        self.user.save()
        self.client.login(email='test@test.org', password='testsecret')

    def tearDown(self):
        for f in Flood.objects.all():
            f.delete()

    def test_process_hazard_layer(self):
        flood = Flood.objects.get(event_id='2015112518-3-rw')
        process_hazard_layer(flood)
