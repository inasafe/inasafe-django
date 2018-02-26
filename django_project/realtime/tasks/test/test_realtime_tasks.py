# coding=utf-8
"""Docstring here."""
import os
import unittest

from django import test

from realtime.tasks.realtime.flood import process_flood
from realtime.tasks.flood import create_flood_report
from realtime.tasks.realtime.celery_app import app as realtime_app

dir_path = os.path.dirname(os.path.realpath(__file__))
flood_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'flood_data.json')


@unittest.skipUnless(
    realtime_app.control.ping(), 'Realtime Worker needs to be run')
class TestRealtimeCeleryTask(test.SimpleTestCase):
    """Unit test for Realtime Celery tasks."""

    def test_create_flood_report(self):
        """Test Create Flood report task"""
        create_flood_report()

    def test_process_flood_manually(self):
        """Test process flood with existing flood json."""
        process_flood.delay(
            flood_id='2018022511-6-rw',
            data_source='hazard_file',
            data_source_args={
                'filename': flood_layer_uri
            }
        )
