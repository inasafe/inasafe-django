# coding=utf-8
"""Docstring here."""
import os
import unittest

from django import test

from realtime.tasks.realtime.flood import process_flood
from realtime.tasks.flood import create_flood_report
from realtime.tasks.realtime.celery_app import app as realtime_app

flood_data_path = '/home/realtime/hazard-drop/flood_data.json'


@unittest.skipUnless(
    realtime_app.control.ping(), 'Realtime Worker needs to be run')
class TestRealtimeCeleryTask(test.SimpleTestCase):
    """Unit test for Realtime Celery tasks."""

    def test_create_flood_report(self):
        """Test Create Flood report task"""
        create_flood_report()

    @unittest.skipUnless(
        os.path.exists(flood_data_path),
        'Skip because this test need flood data in %s' % flood_data_path)
    def test_process_flood_manually(self):
        """Test process flood with existing flood json."""
        process_flood.delay(
            flood_id='2018022411-6-rw',
            data_source='hazard_file',
            data_source_args={
                'filename': flood_data_path
            }
        )
