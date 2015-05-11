# coding=utf-8
"""Model factories definition for models."""
import datetime
import random

from django.contrib.gis.geos import Point

from factory import DjangoModelFactory

from ..models.earthquake import Earthquake


class EarthquakeFactory(DjangoModelFactory):
    """Factory class for Earthquake model."""
    class Meta:
        """Meta definition."""
        model = Earthquake

    time = datetime.datetime.now()
    shake_id = time.strftime('%Y%m%d%H%M%S')
    magnitude = random.uniform(4, 6)
    depth = random.uniform(0, 10)
    location = Point(106.786, -6.598)
    location_description = 'Bogor, Indonesia'
