# coding=utf-8
import logging
import unittest

from django import test
from timeout_decorator import timeout_decorator

from realtime.app_settings import LOGGER_NAME
from realtime.tasks import (
    check_realtime_broker,
    retrieve_felt_earthquake_list)
from realtime.tasks.realtime.celery_app import app as realtime_app
from realtime.utils import celery_worker_connected

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/4/15'


LOGGER = logging.getLogger(LOGGER_NAME)


# minutes test timeout
LOCAL_TIMEOUT = 10 * 60


class CeleryTaskTest(test.SimpleTestCase):

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        celery_worker_connected(realtime_app, 'inasafe-realtime'),
        'Realtime Worker needs to be run')
    def test_indicator(self):
        """Test broker connection."""
        result = check_realtime_broker.delay()
        self.assertTrue(result.get())

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        celery_worker_connected(realtime_app, 'inasafe-django'),
        'Realtime Worker needs to be run')
    def test_retrieve_felt_earthquake(self):
        """Test broker connection."""
        result = retrieve_felt_earthquake_list.delay()
        self.assertTrue(result.get())
