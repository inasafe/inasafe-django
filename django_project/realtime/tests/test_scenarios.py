# coding=utf-8
import errno
import json
import logging
import os
import re
import shutil
import sys
import time
from functools import wraps

import timeout_decorator
import unittest
from datetime import datetime

import pytz
from django import test
from django.apps import apps
from django.core.files.base import File
from django.core.urlresolvers import reverse
from django.utils.translation import activate
from rest_framework import status

from realtime.app_settings import (
    EARTHQUAKE_MONITORED_DIRECTORY,
    LOGGER_NAME,
    REALTIME_HAZARD_DROP, ON_TRAVIS, EARTHQUAKE_CORRECTED_MONITORED_DIRECTORY,
    ANALYSIS_LANGUAGES)
from realtime.models.ash import Ash
from realtime.models.earthquake import Earthquake
from realtime.models.flood import Flood, BoundaryAlias
from realtime.models.volcano import Volcano
from realtime.serializers.earthquake_serializer import EarthquakeSerializer, \
    EarthquakeMMIContourGeoJSONSerializer
from realtime.tasks import RESULT_SUCCESS
from realtime.tasks.flood import create_flood_report
from core.celery_app import app as django_app
from realtime.tasks.realtime.celery_app import app as realtime_app
from realtime.tasks.headless.celery_app import app as headless_app
from realtime.tasks.realtime.flood import process_flood

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = ':%H$'


LOGGER = logging.getLogger(LOGGER_NAME)


FULL_SCENARIO_TEST_CONDITION =(
    # It needs realtime_app worker
    realtime_app.control.ping() and
    # It needs headless_app worker
    headless_app.control.ping() and
    # It needs django_app worker
    django_app.control.ping()
)

# Five minutes test timeout
LOCAL_TIMEOUT = 5 * 60


# Retry decorator for this unittest
def retry(exception, tries=0, delay=5, backoff=2, logger=None):
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exception as e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


class HazardScenarioBaseTestCase(test.LiveServerTestCase):

    def setUp(self):
        super(HazardScenarioBaseTestCase, self).setUp()
        app_config = apps.get_app_config('realtime')
        app_config.create_rest_group()
        app_config.ready()

    @staticmethod
    def fixtures_path(*path):
        return os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../tasks/realtime/test/fixtures', *path))

    def assertContentView(self, view_url, params=None):
        """Assert method for generic view checks.

        :param view_url: URL of the views to check
        :param params: query params for view url
        """
        response = self.client.get(view_url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def content_disposition_filename(self, response):
        """Get filename from content-disposition header."""
        if not response.has_header('content-disposition'):
            return None
        pattern = r'filename="(?P<filename>[\w\-_.]+)"'
        content_disposition = response['content-disposition']
        match = re.search(pattern, content_disposition)
        return match.group('filename')


@unittest.skipUnless(
    FULL_SCENARIO_TEST_CONDITION,
    'All Workers needs to be run')
class TestEarthquakeTasks(HazardScenarioBaseTestCase):

    def assertEarthquake(self, event):
        """Check that earthquake is processed."""
        self.assertTrue(event.hazard_layer_exists)
        self.assertTrue(event.shake_grid_xml)
        self.assertTrue(event.mmi_layer_exists)
        self.assertTrue(event.mmi_layer_saved)

        for lang in ANALYSIS_LANGUAGES:
            event.inspected_language = lang
            self.assertTrue(event.impact_layer_exists)
            self.assertFalse(event.need_run_analysis)

            # Report must be generated
            self.assertTrue(event.has_reports)
            self.assertFalse(event.need_generate_reports)

            # Check django views
            activate(lang)

            # Download MMI contours
            mmi_contour_download_url = reverse(
                'realtime:earthquake_mmi_contours_list',
                kwargs={
                    'shake_id': event.shake_id,
                    'source_type': event.source_type
                }
            )
            params = {
                'format': 'json'
            }

            response = self.assertContentView(
                mmi_contour_download_url,
                params)
            geojson_obj = json.loads(response.content)
            contours_count = len(geojson_obj['features'])

            self.assertEqual(
                event.contours.all().count(), contours_count)

            # Download grid xml
            grid_xml_download_url = reverse(
                'realtime:shake_grid',
                kwargs={
                    'shake_id': event.shake_id,
                    'source_type': event.source_type
                }
            )
            response = self.assertContentView(grid_xml_download_url)

            self.assertEqual(
                response.content, event.shake_grid_xml)
            self.assertEqual(
                response['content-type'],
                'application/octet-stream')
            self.assertEqual(
                self.content_disposition_filename(response),
                event.grid_xml_filename)

            # Download report
            report_download_url = reverse(
                'realtime:earthquake_report_detail',
                kwargs={
                    'shake_id': event.shake_id,
                    'source_type': event.source_type,
                    'language': lang
                }
            )

            response = self.assertContentView(report_download_url)
            json_obj = json.loads(response.content)
            self.assertTrue(json_obj['report_pdf'])

            response = self.assertContentView(json_obj['report_pdf'])
            self.assertEqual(
                event.report_object.report_pdf.size,
                int(response['content-length']))

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    def test_process_earthquake(self):
        """Test generating earthquake scenarios."""
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

        # Assumming all process runs normally we should expects all asserts
        # will eventually passed.
        bigint = sys.maxint
        kwargs = {
            'exception': BaseException,
            'tries': bigint,
            'delay': 5,
            'backoff': 1,
            'logger': LOGGER
        }

        @retry(**kwargs)
        def loop_check(test_obj, shake_id, source_type):
            """This method will always loop until it succeeds.

            :type test_obj: HazardScenarioBaseTestCase
            :type shake_id: str
            :type source_type: str
            """

            event = Earthquake.objects.get(
                shake_id=shake_id,
                source_type=source_type)
            """:type: Earthquake"""

            # Check that report is generated
            for lang in ANALYSIS_LANGUAGES:

                event.inspected_language = lang

                # Report must be generated
                self.assertTrue(event.has_reports)
                self.assertFalse(event.need_generate_reports)

            return event

        initial_event = loop_check(
            self, '20180220163351', Earthquake.INITIAL_SOURCE_TYPE)

        initial_event.refresh_from_db()

        self.assertEarthquake(initial_event)

        corrected_event = loop_check(
            self, '20180220162928_50_01400_124450_20180220162928',
            Earthquake.CORRECTED_SOURCE_TYPE)

        corrected_event.refresh_from_db()

        self.assertEarthquake(corrected_event)

        # Initial event should have reference for corrected event
        initial_event.refresh_from_db()

        self.assertEqual(
            initial_event.corrected_shakemaps,
            corrected_event)

        # Corrected event should have reference to initial event
        self.assertEqual(
            corrected_event.initial_shakemaps,
            initial_event)

        # Check cache flag
        self.assertTrue(initial_event.has_corrected)
        self.assertFalse(corrected_event.has_corrected)

        # Check django view return correct object
        response = self.client.get(
            reverse('realtime:shake_corrected', kwargs={
                'shake_id': initial_event.shake_id,
            }))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        actual_value = json.loads(response.content)
        # omit shake grid field because it is not a file
        actual_value.pop('shake_grid')

        eq_serializer = EarthquakeSerializer(corrected_event)
        expected_value = json.loads(json.dumps(eq_serializer.data))
        expected_value.pop('shake_grid')
        self.assertEqual(actual_value, expected_value)


@unittest.skipUnless(
    FULL_SCENARIO_TEST_CONDITION and False,
    'All Workers needs to be run')
class TestAshTasks(test.LiveServerTestCase):

    def setUp(self):
        super(TestAshTasks, self).setUp()
        app_config = apps.get_app_config('realtime')
        app_config.create_rest_group()
        app_config.ready()

    @staticmethod
    def fixtures_path(*path):
        return os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '../tasks/realtime/test/fixtures', *path))

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
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

        # wait until analysis were processed
        while not ash.impact_layer_exists:
            ash.refresh_from_db()
            LOGGER.info('Waiting for Headless Analysis')
            time.sleep(5)

        # Check impact location
        self.assertTrue(ash.impact_layer_exists)

        # Check analysis status
        self.assertEqual(ash.analysis_task_result['status'], RESULT_SUCCESS)

        # wait until reports were generated
        while not ash.has_reports > 0:
            ash.refresh_from_db()
            LOGGER.info('Waiting for Headless Report')
            time.sleep(5)

        # Check reports exists
        self.assertTrue(ash.has_reports)
        self.assertEqual(ash.reports.first().report_map)

        ash.delete()
