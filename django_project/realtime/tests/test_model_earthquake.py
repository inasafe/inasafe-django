# coding=utf-8
"""Module related to test for all the models in realtime apps."""
from django.test import TestCase

from realtime.tests.model_factories import EarthquakeFactory


class TestEarthquake(TestCase):
    """Class to test Earthquake model."""
    def setUp(self):
        pass

    def test_create_earthquake(self):
        """Method to test earthquake object creation."""
        earthquake = EarthquakeFactory.create()
        message = 'The earthquake object is instantiated successfully.'
        self.assertIsNotNone(earthquake.id, message)

    def test_read_earthquake(self):
        """Method to test reading earthquake object."""
        location_description = 'Bandung, Indonesia'
        earthquake = EarthquakeFactory.create(
            location_description=location_description)
        message = 'The location description should be %s, but it gives %s' % (
            location_description, earthquake.location_description)
        self.assertEqual(
            location_description, earthquake.location_description, message)

    def test_update_earthquake(self):
        """Method to test updating earthquake."""
        earthquake = EarthquakeFactory.create()
        location_description = 'Updated location description'
        earthquake.location_description = location_description
        earthquake.save()
        message = 'The location description should be %s, but it gives %s' % (
            location_description, earthquake.location_description)
        self.assertEqual(
            location_description, earthquake.location_description, message)

    def test_delete_earthquake(self):
        """Method to test deleting earthquake."""
        earthquake = EarthquakeFactory.create()
        self.assertIsNotNone(earthquake.id)
        earthquake.delete()
        message = 'The earthquake instance is not deleted.'
        self.assertIsNone(earthquake.id, message)
