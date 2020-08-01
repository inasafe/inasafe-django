# coding=utf-8
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
import io
import errno
import json
import logging
import os
import re
import shutil
import sys
import time
import unittest
from datetime import datetime
from functools import wraps

import pytz
import timeout_decorator
from django import test
from django.apps import apps
from django.core import management
from django.core.files.base import File
from django.core.urlresolvers import reverse
from django.utils.translation import activate
from mock import patch, MagicMock
from rest_framework import status

from core.celery_app import app as django_app
from realtime.app_settings import (
    EARTHQUAKE_MONITORED_DIRECTORY,
    LOGGER_NAME,
    REALTIME_HAZARD_DROP, EARTHQUAKE_CORRECTED_MONITORED_DIRECTORY,
    ANALYSIS_LANGUAGES)
from realtime.models import FloodEventBoundary
from realtime.models.ash import Ash, AshReport
from realtime.models.earthquake import Earthquake, EarthquakeReport
from realtime.models.flood import Flood, BoundaryAlias, FloodReport, \
    ImpactEventBoundary
from realtime.models.impact import Impact
from realtime.models.volcano import Volcano
from realtime.serializers.earthquake_serializer import EarthquakeSerializer
from realtime.tasks.earthquake import push_shake_to_inaware
from realtime.tasks.headless.celery_app import app as headless_app
from realtime.tasks.realtime.celery_app import app as realtime_app
from realtime.tasks.realtime.flood import process_flood
from realtime.utils import celery_worker_connected

LOGGER = logging.getLogger(LOGGER_NAME)


# minutes test timeout
LOCAL_TIMEOUT = 10 * 60


def check_full_scenario_test_condition():
    """Check all workers online at runtime."""
    return (
        # It needs realtime_app worker
        celery_worker_connected(realtime_app, 'inasafe-realtime')
        # It needs headless_app worker
        and celery_worker_connected(headless_app, 'inasafe-headless')
        # It needs django_app worker
        and celery_worker_connected(django_app, 'inasafe-django')
    )


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
        pattern = r'filename="(?P<filename>[\w\+\-_.]+)"'
        content_disposition = response['content-disposition']
        match = re.search(pattern, content_disposition)
        return match.group('filename')


class BaseTestEarthquakeTasks(HazardScenarioBaseTestCase):

    # Assumming all process runs normally we should expects all asserts
    # will eventually passed.
    bigint = sys.maxsize
    retry_kwargs = {
        'exception': BaseException,
        'tries': bigint,
        'delay': 5,
        'backoff': 1,
        'logger': LOGGER
    }

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
                event.canonical_report_pdf.size,
                int(response['content-length']))

    @retry(**retry_kwargs)
    def loop_check(self, shake_id, source_type):
        """This method will always loop until it succeeds.

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


class TestEarthquakeTasks(BaseTestEarthquakeTasks):

    class InAWARERestMock(MagicMock):

        def get_hazard_id(self, shake_id):
            """Arbitrary hazard ID returned by InAWARE"""
            return 123

        def post_url_product(
                self, hazard_id, url_product, title='Automated URL Product'):
            """Do nothing. Emulate successful post"""
            return True

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        check_full_scenario_test_condition(),
        'All Workers needs to be run')
    def test_process_earthquake(self):
        """Test generating earthquake scenarios."""
        # Drop a grid file to monitored directory
        grid_file = self.fixtures_path('20180220163351-grid.xml')

        drop_location_initial = os.path.join(
            EARTHQUAKE_MONITORED_DIRECTORY,
            '20180220163351',
            'grid.xml')

        try:
            os.makedirs(os.path.dirname(drop_location_initial))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass

        shutil.copy(grid_file, drop_location_initial)

        initial_event = self.loop_check(
            '20180220163351', Earthquake.INITIAL_SOURCE_TYPE)

        initial_event.refresh_from_db()

        self.assertEarthquake(initial_event)

        # Test dropping a corrected shakemaps
        grid_file = self.fixtures_path(
            '20180220162928_50_01400_124450_20180220162928-grid.xml')

        drop_location_corrected = os.path.join(
            EARTHQUAKE_CORRECTED_MONITORED_DIRECTORY,
            '20180220162928_50_01400_124450_20180220162928',
            'grid.xml')

        try:
            os.makedirs(os.path.dirname(drop_location_corrected))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass

        shutil.copy(grid_file, drop_location_corrected)

        corrected_event = self.loop_check(
            '20180220162928_50_01400_124450_20180220162928',
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

        # Test InAWARE push using mock
        with patch(
                'realtime.tasks.earthquake.InAWARERest',
                new=self.InAWARERestMock):
            result = push_shake_to_inaware(
                initial_event.shake_id,
                initial_event.source_type)
            self.assertTrue(result)

        initial_event.delete()
        corrected_event.delete()

        os.remove(drop_location_initial)
        os.remove(drop_location_corrected)

        # Make sure reports and impacts were also deleted.
        self.assertEqual(0, Earthquake.objects.all().count())
        self.assertEqual(0, Impact.objects.all().count())
        self.assertEqual(0, EarthquakeReport.objects.all().count())


class TestEarthquakeCheckProcessedTasks(BaseTestEarthquakeTasks):

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        check_full_scenario_test_condition(),
        'All Workers needs to be run')
    def test_checkprocessedeq_command(self):
        """Test checkprocessedeq management command."""
        # Drop a grid file to monitored directory
        grid_file = self.fixtures_path('20180220163351-grid.xml')

        drop_location_initial = os.path.join(
            EARTHQUAKE_MONITORED_DIRECTORY,
            '20180220163351',
            'grid.xml')

        try:
            os.makedirs(os.path.dirname(drop_location_initial))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass

        shutil.copy(grid_file, drop_location_initial)

        initial_event = self.loop_check(
            '20180220163351', Earthquake.INITIAL_SOURCE_TYPE)

        initial_event.refresh_from_db()

        self.assertEarthquake(initial_event)

        # Check that running checkprocessedeq will return a clean results
        out = io.StringIO()
        management.call_command(
            'checkprocessedeq',
            since='2018/02/19',
            dry_run=False,
            stdout=out)

        output_messages = out.getvalue()

        # All shake should have been processed
        self.assertIn('Total Unprocessed impacts (0)', output_messages)

        # All reports should be generated
        self.assertIn('Total Unprocessed reports (0)', output_messages)

        # Clear out report generation flag
        for lang in ANALYSIS_LANGUAGES:

            initial_event.inspected_language = lang
            initial_event.report_object.delete()

        # Command needs to recognize missing reports
        out = io.StringIO()
        management.call_command(
            'checkprocessedeq',
            since='2018/02/19',
            dry_run=False,
            stdout=out)

        output_messages = out.getvalue()

        self.assertIn('Total Unprocessed reports (2)', output_messages)

        # This should pass
        initial_event = self.loop_check(
            '20180220163351', Earthquake.INITIAL_SOURCE_TYPE)

        self.assertTrue(initial_event.has_reports)

        # Clear out impact layers
        for lang in ANALYSIS_LANGUAGES:

            initial_event.inspected_language = lang
            impact_dirname = os.path.dirname(
                initial_event.impact_file_path)
            shutil.rmtree(impact_dirname, ignore_errors=True)
            self.assertFalse(os.path.exists(impact_dirname))

        # Command needs to ignore missing impacts when reports were processed.
        out = io.StringIO()
        management.call_command(
            'checkprocessedeq',
            since='2018/02/19',
            dry_run=False,
            stdout=out)

        output_messages = out.getvalue()

        self.assertIn('Total Unprocessed reports (0)', output_messages)

        # However if we delete the reports it should recognized missing
        # impacts
        # Clear out report generation flag
        for lang in ANALYSIS_LANGUAGES:

            initial_event.inspected_language = lang
            initial_event.report_object.delete()

        # Command needs to recognize missing reports
        out = io.StringIO()
        management.call_command(
            'checkprocessedeq',
            since='2018/02/19',
            dry_run=False,
            stdout=out)

        output_messages = out.getvalue()

        self.assertIn('Total Unprocessed reports (2)', output_messages)

        # also recognized missing impacts
        self.assertIn('Total Unprocessed impacts (2)', output_messages)

        # Reports needs to be generated
        initial_event = self.loop_check(
            '20180220163351', Earthquake.INITIAL_SOURCE_TYPE)

        self.assertTrue(initial_event.has_reports)

        initial_event.delete()

        os.remove(drop_location_initial)


class TestFloodTasks(HazardScenarioBaseTestCase):

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        check_full_scenario_test_condition(),
        'All Workers needs to be run')
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

        # Assumming all process runs normally we should expects all asserts
        # will eventually passed.
        bigint = sys.maxsize
        kwargs = {
            'exception': BaseException,
            'tries': bigint,
            'delay': 5,
            'backoff': 1,
            'logger': LOGGER
        }

        @retry(**kwargs)
        def loop_check(self, event_id):
            """This method will always loop until it succeeds.

            :type self: HazardScenarioBaseTestCase
            :type event_id: str
            """
            event = Flood.objects.get(event_id=event_id)
            ":type: Flood"

            # Check that report is generated
            for lang in ANALYSIS_LANGUAGES:

                event.inspected_language = lang

                # Report must be generated
                self.assertTrue(event.has_reports)
                self.assertFalse(event.need_generate_reports)

            return event

        flood_event = loop_check(self, '2018022511-6-rw')
        flood_event.refresh_from_db()

        self.assertTrue(flood_event.hazard_layer_exists)
        self.assertEqual(161, flood_event.boundary_flooded)
        self.assertEqual(12998562, flood_event.total_affected)
        self.assertTrue(flood_event.flooded_boundaries.all())

        self.assertEqual(
            0,
            flood_event.flooded_boundaries.filter(
                flood_event__hazard_data=0).count())
        self.assertEqual(
            3,
            flood_event.flooded_boundaries.filter(
                flood_event__hazard_data=1).count())
        self.assertEqual(
            151,
            flood_event.flooded_boundaries.filter(
                flood_event__hazard_data=2).count())
        self.assertEqual(
            7,
            flood_event.flooded_boundaries.filter(
                flood_event__hazard_data=3).count())

        self.assertEqual(1064, flood_event.impact_event.count())

        for lang in ANALYSIS_LANGUAGES:
            flood_event.inspected_language = lang

            self.assertTrue(flood_event.impact_layer_exists)
            self.assertFalse(flood_event.need_run_analysis)

            # Report must be generated
            self.assertTrue(flood_event.has_reports)
            self.assertFalse(flood_event.need_generate_reports)

            # Check django views
            activate(lang)

            # Download Flood hazard
            flood_hazard_download_url = reverse(
                'realtime:flood_data',
                kwargs={
                    'event_id': flood_event.event_id
                }
            )
            params = {
                'format': 'json'
            }

            response = self.assertContentView(
                flood_hazard_download_url,
                params)

            flood_data = json.loads(response.content)
            self.assertEqual(
                flood_event.flooded_boundaries.all().count(),
                len(flood_data['features']))

            # Download Report
            report_download_url = reverse(
                'realtime:flood_impact_map',
                kwargs={
                    'event_id': flood_event.event_id,
                    'language': lang
                }
            )

            response = self.assertContentView(report_download_url)

            self.assertEqual(
                response['content-type'], 'application/pdf')
            self.assertEqual(
                self.content_disposition_filename(response),
                flood_event.canonical_report_filename)
            self.assertEqual(
                len(response.content),
                flood_event.canonical_report_pdf.size)

        flood_event.delete()

        # Make sure reports and impacts were also deleted.
        self.assertEqual(0, Flood.objects.all().count())
        self.assertEqual(0, Impact.objects.all().count())
        self.assertEqual(0, FloodEventBoundary.objects.all().count())
        self.assertEqual(0, ImpactEventBoundary.objects.all().count())
        self.assertEqual(0, FloodReport.objects.all().count())


class TestAshTasks(HazardScenarioBaseTestCase):

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        check_full_scenario_test_condition(),
        'All Workers needs to be run')
    def test_process_ash(self):
        """Test generating ash hazard."""
        # Create an ash object
        volcano = Volcano.objects.get(volcano_name='Sinabung')

        time_zone = pytz.timezone('Asia/Jakarta')
        event_time = datetime(2018, 3, 23, 16, 36, tzinfo=pytz.utc)
        event_time = event_time.astimezone(time_zone)

        ash = Ash.objects.create(
            hazard_file=File(open(self.fixtures_path(
                '201803231636+0700_Sinabung-hazard.tif'))),
            volcano=volcano,
            alert_level='normal',
            event_time=event_time,
            event_time_zone_offset=420,
            event_time_zone_string='Asia/Jakarta',
            eruption_height=100,
            forecast_duration=3)

        # Assumming all process runs normally we should expects all asserts
        # will eventually passed.
        bigint = sys.maxsize
        kwargs = {
            'exception': BaseException,
            'tries': bigint,
            'delay': 5,
            'backoff': 1,
            'logger': LOGGER
        }

        @retry(**kwargs)
        def loop_check(self, event_id):
            """This method will always loop until it succeeds.

            :type self: HazardScenarioBaseTestCase
            :type event_id: str
            """
            event = Ash.objects.get(id=event_id)
            ":type: Ash"

            # Check that report is generated
            for lang in ANALYSIS_LANGUAGES:

                event.inspected_language = lang

                # Report must be generated
                self.assertTrue(event.hazard_layer_exists)
                self.assertTrue(event.has_reports)
                self.assertFalse(event.need_generate_reports)

            return event

        event = loop_check(self, ash.id)
        event.refresh_from_db()

        self.assertTrue(event.hazard_layer_exists)

        for lang in ANALYSIS_LANGUAGES:
            event.inspected_language = lang

            self.assertTrue(event.impact_layer_exists)
            self.assertFalse(event.need_run_analysis)

            # Report must be generated
            self.assertTrue(event.has_reports)
            self.assertFalse(event.need_generate_reports)

            # Check django views
            activate(lang)

            # Download Flood hazard
            ash_detail_url = reverse(
                'realtime:ash_detail',
                kwargs={
                    'volcano_name': event.volcano.volcano_name,
                    'event_time': event.event_time_formatted
                }
            )
            params = {
                'format': 'json'
            }

            response = self.assertContentView(
                ash_detail_url,
                params)

            ash_data = json.loads(response.content)

            ash_hazard_url = ash_data['hazard_file']
            response = self.assertContentView(ash_hazard_url)

            self.assertEqual(
                response['content-type'],
                'image/tiff')
            self.assertEqual(
                int(response['content-length']),
                event.hazard_file.size)

            # Download Report
            report_download_url = reverse(
                'realtime:ash_report_map',
                kwargs={
                    'volcano_name': event.volcano.volcano_name,
                    'event_time': event.event_time_formatted,
                    'language': lang
                }
            )

            response = self.assertContentView(report_download_url)

            self.assertEqual(
                response['content-type'], 'application/pdf')
            self.assertEqual(
                self.content_disposition_filename(response),
                event.canonical_report_filename)
            self.assertEqual(
                len(response.content),
                event.canonical_report_pdf.size)

        ash.delete()

        self.assertEqual(0, Ash.objects.all().count())
        self.assertEqual(0, Impact.objects.all().count())
        self.assertEqual(0, AshReport.objects.all().count())
