# coding=utf-8
from datetime import datetime

import os
import pytz
from django import test
from django.apps import apps
from django.core.files.base import File

from realtime.models.ash import Ash
from realtime.models.volcano import Volcano

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = ':%H$'


class TestAshTasks(test.SimpleTestCase):

    def setUp(self):
        app_config = apps.get_app_config('realtime')
        app_config.load_volcano_fixtures()

    @staticmethod
    def fixtures_path(*path):
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'fixtures', *path))

    def test_process_ash(self):
        """Test generating ash hazard."""
        # Create an ash object
        volcano = Volcano.objects.get(volcano_name='Merapi')

        time_zone = pytz.timezone('Asia/Jakarta')
        event_time = datetime(2017, 2, 21, 12, 4, tzinfo=pytz.utc)
        event_time = event_time.astimezone(time_zone)

        ash = Ash.objects.create(
            hazard_file=File(open(self.fixtures_path(
                '201702211204+0000_Merapi-hazard.tif'))),
            volcano=volcano,
            alert_level='normal',
            event_time=event_time,
            event_time_zone_offset=420,
            event_time_zone_string='Asia/Jakarta',
            eruption_height=100,
            forecast_duration=3)

        ash.delete()
