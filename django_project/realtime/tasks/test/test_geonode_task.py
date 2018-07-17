# coding=utf-8
import os
from unittest import skip
from django.test import TestCase

from realtime.tasks.geonode import push_hazard_to_geonode
from realtime.models.flood import Flood
from realtime.tests.model_factories import FloodFactory


class TestModelFlood(TestCase):

    @skip('Under development')
    def test_upload_flood_hazard(self):
        flood = FloodFactory.create()
        message = 'The flood object is instantiated successfully.'
        self.assertIsNotNone(flood.id, message)
        self.assertTrue(os.path.exists(flood.hazard_path))
        async_result = push_hazard_to_geonode.delay(Flood, flood)
        _ = async_result.get()  # noqa
