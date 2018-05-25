# coding=utf-8
import os

from django.test import TestCase

from realtime.tests.model_factories import FloodFactory

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '11/25/15'


class TestModelFlood(TestCase):

    def test_create_flood(self):
        flood = FloodFactory.create()
        message = 'The flood object is instantiated successfully.'
        self.assertIsNotNone(flood.id, message)
        self.assertTrue(os.path.exists(flood.hazard_path))
