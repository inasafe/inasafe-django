# coding=utf-8
import errno
import logging
import os
import shutil
import time
import unittest
from datetime import datetime

import pytz
import timeout_decorator
from django import test
from django.apps import apps
from django.core.files.base import File
from realtime.utils import celery_worker_connected

from realtime.app_settings import (
    EARTHQUAKE_MONITORED_DIRECTORY,
    LOGGER_NAME,
    REALTIME_HAZARD_DROP, ON_TRAVIS, EARTHQUAKE_CORRECTED_MONITORED_DIRECTORY)
from realtime.models.ash import Ash
from realtime.models.earthquake import Earthquake
from realtime.models.flood import Flood, BoundaryAlias
from realtime.models.volcano import Volcano
from realtime.tasks.flood import create_flood_report
from realtime.tasks.realtime.celery_app import app as realtime_app
from realtime.tasks.realtime.flood import process_flood

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = ':%H$'


LOGGER = logging.getLogger(LOGGER_NAME)

# minutes test timeout
LOCAL_TIMEOUT = 10 * 60


class TestAshTasks(test.LiveServerTestCase):

    def setUp(self):
        super(TestAshTasks, self).setUp()
        app_config = apps.get_app_config('realtime')
        app_config.create_rest_group()
        app_config.ready()

    @staticmethod
    def fixtures_path(*path):
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'fixtures', *path))

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        celery_worker_connected(realtime_app, 'inasafe-realtime'),
        'Realtime Worker needs to be run')
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

        # wait until hazard file is processed
        while not ash.hazard_layer_exists:
            ash.refresh_from_db()
            LOGGER.info('Waiting for Realtime Hazard Push')
            time.sleep(5)

        # Check hazard information pushed to db
        self.assertTrue(ash.hazard_layer_exists)

        ash.delete()


class TestEarthquakeTasks(test.LiveServerTestCase):

    def setUp(self):
        super(TestEarthquakeTasks, self).setUp()
        app_config = apps.get_app_config('realtime')
        app_config.create_rest_group()
        app_config.ready()

    @staticmethod
    def fixtures_path(*path):
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'fixtures', *path))

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        celery_worker_connected(realtime_app, 'inasafe-realtime'),
        'Realtime Worker needs to be run')
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
                target_event = Earthquake.objects.get(
                    shake_id='20180220163351',
                    source_type=Earthquake.INITIAL_SOURCE_TYPE)
                if (target_event.hazard_layer_exists
                        and target_event.shake_grid_xml):
                    break
            except BaseException:
                pass

            LOGGER.info('Waiting for Realtime Hazard push')
            time.sleep(5)

        self.assertTrue(target_event.hazard_layer_exists)
        self.assertTrue(target_event.shake_grid_xml)

        initial_event = target_event

        # Test dropping a corrected shakemaps
        grid_file = self.fixtures_path(
            '20180220162928_50_01400_124450_20180220162928-grid.xml')

        drop_location = os.path.join(
            EARTHQUAKE_CORRECTED_MONITORED_DIRECTORY,
            '20180220162928_50_01400_124450_20180220162928',
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
                target_event = Earthquake.objects.get(
                    shake_id='20180220162928_50_01400_124450_20180220162928',
                    source_type=Earthquake.CORRECTED_SOURCE_TYPE)
                if (target_event.hazard_layer_exists
                        and target_event.shake_grid_xml):
                    break
            except BaseException:
                pass

            LOGGER.info('Waiting for Realtime Hazard push')
            time.sleep(5)

        self.assertTrue(target_event.hazard_layer_exists)
        self.assertTrue(target_event.shake_grid_xml)

        # Check that corrected shakemaps can be requested from initial
        # shakemaps
        initial_event.refresh_from_db()
        self.assertTrue(initial_event.has_corrected)
        target_event.refresh_from_db()
        self.assertEqual(target_event, initial_event.corrected_shakemaps)

        initial_event.delete()
        target_event.delete()


class TestFloodTasks(test.LiveServerTestCase):
    """Unit test for Realtime Celery tasks."""

    def setUp(self):
        super(TestFloodTasks, self).setUp()
        app_config = apps.get_app_config('realtime')
        app_config.create_rest_group()
        app_config.ready()

    @staticmethod
    def fixtures_path(*path):
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'fixtures', *path))

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipIf(
        ON_TRAVIS,
        'We do not want to abuse PetaBencana Server.')
    @unittest.skipUnless(
        celery_worker_connected(realtime_app, 'inasafe-realtime'),
        'Realtime Worker needs to be run')
    def test_create_flood_report(self):
        """Test Create Flood report task"""
        create_flood_report()

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        celery_worker_connected(realtime_app, 'inasafe-realtime'),
        'Realtime Worker needs to be run')
    def test_process_flood_manually(self):
        """Test process flood with existing flood json."""
        # check boundary alias exists
        self.assertTrue(BoundaryAlias.objects.all().count() > 0)

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

        # Wait until hazard is pushed
        while True:
            try:
                target_event = Flood.objects.get(event_id='2018022511-6-rw')

                if target_event.hazard_layer_exists:
                    break
            except BaseException as e:
                LOGGER.exception(e)

            LOGGER.info('Waiting for Realtime Hazard push')
            time.sleep(5)

        self.assertTrue(target_event.hazard_layer_exists)

        target_event.delete()
