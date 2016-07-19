# coding=utf-8
"""Model factories definition for models."""
import datetime
import random

from django.contrib.gis.geos import Point
from django.contrib.gis.geos import Polygon
from factory.django import DjangoModelFactory

from realtime.models.earthquake import Earthquake
from realtime.models.flood import Boundary, Flood


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


class BoundaryFactory(DjangoModelFactory):
    """Factory class for Boundary model."""
    class Meta:
        """Meta class"""
        model = Boundary

    upstream_id = '3171010001001000'
    name = 'RW 01'
    geometry = Polygon(
        ((106.926642999777, -6.10361499981753),
         (106.926679999685, -6.10472499974411),
         (106.92662844335, -6.10473051348752),
         (106.926628400331, -6.10473051808828),
         (106.925773000126, -6.10482199972061),
         (106.925746999827, -6.10469900034369),
         (106.925588999735, -6.10396899995448),
         (106.925207000105, -6.1037230003013),
         (106.924755999992, -6.10343300041772),
         (106.924865999668, -6.10273399965946),
         (106.924889999876, -6.10236000039874),
         (106.924105999694, -6.10233600019131),
         (106.924278000432, -6.10015400029193),
         (106.924632999716, -6.10003200006175),
         (106.925294999667, -6.10003200006175),
         (106.92578499978, -6.09998300050009),
         (106.926311999801, -6.09963000040924),
         (106.926618999569, -6.10216500039956),
         (106.926642999777, -6.10361499981753))
    )


class FloodFactory(DjangoModelFactory):
    class Meta:
        model = Flood

    event_id = '2015112518-6-rw'
    time = datetime.datetime.now()
    interval = 6
    source = 'PetaJakarta'
