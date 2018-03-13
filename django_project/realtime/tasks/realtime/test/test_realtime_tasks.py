# coding=utf-8
import errno
import logging
import os
import shutil
import time
import unittest
from datetime import datetime

import pytz
from celery.result import AsyncResult
from django import test
from django.apps import apps
from django.core.files.base import File

from realtime.app_settings import (
    EARTHQUAKE_MONITORED_DIRECTORY,
    LOGGER_NAME,
    REALTIME_HAZARD_DROP)
from realtime.models.ash import Ash
from realtime.models.earthquake import Earthquake
from realtime.models.volcano import Volcano
from realtime.tasks.flood import create_flood_report
from realtime.tasks.realtime.celery_app import app as realtime_app
from realtime.tasks.realtime.flood import process_flood

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = ':%H$'


LOGGER = logging.getLogger(LOGGER_NAME)


@unittest.skipUnless(
    realtime_app.control.ping(),
    'Realtime Worker needs to be run')
class TestAshTasks(test.LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestAshTasks, cls).setUpClass()
        app_config = apps.get_app_config('realtime')
        app_config.create_rest_group()
        app_config.ready()

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

        # force synchronous result
        ash.refresh_from_db()
        result = AsyncResult(id=ash.task_id, app=realtime_app)
        actual_value = result.get()
        ash.refresh_from_db()

        # Check state
        self.assertEqual(result.state, 'SUCCESS')

        # Check ret_val
        expected_value = {
            'hazard_path': '/home/realtime/ashmaps/201702211904+0700_Merapi/'
                           'ash_fall.tif',
            'success': True
        }
        self.assertEqual(expected_value, actual_value)

        # Check hazard information pushed to db
        self.assertTrue(ash.hazard_layer_exists)

        from realtime.tasks.ash import check_processing_task

        result = check_processing_task.delay()
        result.get()

        ash.refresh_from_db()

        # TODO: Fixme. Somehow the following asserts produces an error
        # It was not supposed to do that.
        # Check that the same task has been marked as success.
        # result = AsyncResult(id=ash.task_id, app=realtime_app)
        # self.assertEqual(result.state, 'SUCCESS')
        # self.assertEqual(ash.task_status, 'SUCCESS')

        ash.delete()


@unittest.skipUnless(
    realtime_app.control.ping(),
    'Realtime Worker needs to be run')
class TestEarthquakeTasks(test.LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestEarthquakeTasks, cls).setUpClass()
        app_config = apps.get_app_config('realtime')
        app_config.create_rest_group()
        app_config.ready()

    @staticmethod
    def fixtures_path(*path):
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'fixtures', *path))

    def test_process_earthquake(self):
        """Test generating earthquake hazard."""
        # Drop a grid file to monitored directory
        grid_file = self.fixtures_path('20180220163351-grid.xml')

        drop_location = os.path.join(
            EARTHQUAKE_MONITORED_DIRECTORY,
            '20180220163351',
            'grid.xml')

        try:
            os.makedirs(os.path.dirname(drop_location))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass

        shutil.copy(grid_file, drop_location)

        # wait until grid file is processed
        while True:
            try:
                target_eq = Earthquake.objects.get(
                    shake_id='20180220163351',
                    source_type='initial')
                if target_eq.hazard_layer_exists and target_eq.shake_grid_xml:
                    break
            except BaseException:
                pass

            LOGGER.info('Waiting for Realtime EQ push')
            time.sleep(5)

        self.assertTrue(target_eq.hazard_layer_exists)
        self.assertTrue(target_eq.shake_grid_xml)

        target_eq.delete()


@unittest.skipUnless(
    realtime_app.control.ping(), 'Realtime Worker needs to be run')
class TestRealtimeCeleryTask(test.SimpleTestCase):
    """Unit test for Realtime Celery tasks."""

    @staticmethod
    def fixtures_path(*path):
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'fixtures', *path))

    def test_create_flood_report(self):
        """Test Create Flood report task"""
        create_flood_report()

    def test_process_flood_manually(self):
        """Test process flood with existing flood json."""

        flood_json = self.fixtures_path('flood_data.json')

        drop_location = os.path.join(
            REALTIME_HAZARD_DROP,
            'flood_data.json')

        try:
            os.makedirs(os.path.dirname(drop_location))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass

        shutil.copy(flood_json, drop_location)

        process_flood.delay(
            flood_id='2018022511-6-rw',
            data_source='hazard_file',
            data_source_args={
                'filename': drop_location
            }
        )
