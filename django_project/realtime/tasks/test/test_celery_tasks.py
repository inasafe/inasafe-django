# coding=utf-8
import logging

from django import test

from realtime.app_settings import LOGGER_NAME
from realtime.tasks import check_realtime_broker

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/4/15'


LOGGER = logging.getLogger(LOGGER_NAME)


class CeleryTaskTest(test.SimpleTestCase):

    def test_indicator(self):
        """Test broker connection."""
        result = check_realtime_broker.delay()
        self.assertTrue(result.get())
