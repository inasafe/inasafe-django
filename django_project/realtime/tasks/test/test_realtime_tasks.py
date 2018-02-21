# coding=utf-8
"""Docstring here."""
import unittest
from django import test

from realtime.tasks.realtime.flood import process_flood
from realtime.tasks.flood import create_flood_report
from realtime.tasks.realtime.celery_app import app as realtime_app


@unittest.skipUnless(
    realtime_app.control.ping(), 'Realtime Worker needs to be run')
class TestRealtimeCeleryTask(test.SimpleTestCase):
    """Unit test for Realtime Celery tasks."""

    def test_process_flood(self):
        """Test process flood."""
        async_result = process_flood.delay()
        result = async_result.get()
        self.assertTrue(result['success'])

    def test_create_flood_report(self):
        """Test Create Flood report task"""
        create_flood_report()
