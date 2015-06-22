# coding=utf-8
import datetime

from django.contrib.gis.geos.point import Point
from django.core.files.base import File
from django.test import TestCase
import os
import pytz
from realtime.models.earthquake import Earthquake, EarthquakeReport
from realtime.views.earthquake import earthquake_list
from django.core.urlresolvers import reverse
from rest_framework.test import APIRequestFactory

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '20/06/15'


class TestEarthquake(TestCase):

    factory = APIRequestFactory()

    def setUp(self):
        Earthquake.objects.create(
            shake_id='20150619200628',
            magnitude=4.6,
            time=datetime.datetime(
                2015, 6, 19, 20, 6, 28,
                tzinfo=pytz.timezone('Asia/Jakarta')),
            depth=10,
            location=Point(x=126.52, y=4.16, srid=4326),
            location_description='Manado'
        )
        earthquake = Earthquake.objects.get(shake_id='20150619200628')
        earthquake.save()
        report_pdf = earthquake.shake_id+'-id.pdf'
        report_png = earthquake.shake_id+'-id.png'
        report_thumb = earthquake.shake_id+'-thumb-id.png'
        report = EarthquakeReport()
        report.earthquake = earthquake
        print os.getcwd()
        with open('realtime/tests/data/'+report_pdf) as pdf:
            report.report_pdf = File(pdf)
            report.save()
        with open('realtime/tests/data/'+report_png) as png:
            report.report_image = File(png)
            report.save()
        with open('realtime/tests/data/'+report_thumb) as thumb:
            report.report_thumbnail = File(thumb)
            report.save()

    def test_earthquake_list(self):
        request = self.factory.get(reverse('realtime:earthquake_list'))
        response = earthquake_list(request)
        expected_shake_id = '20150619200628'
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['shake_id'], expected_shake_id)

    def test_earthquake_detail(self):
        request = self.factory.get(reverse(
            'realtime:earthquake_detail',
            kwargs={'shake_id': '20150619200628'}))
        response = earthquake_list(request)
        expected_earthquake = {
            'shake_id': '20150619200628',
            'magnitude': 4.6,
            'depth': 10,
            'location_description': 'Manado'
        }
        actual_earthquake = response.data[0]
        for key, value in expected_earthquake.iteritems():
            self.assertEqual(actual_earthquake[key], value)
