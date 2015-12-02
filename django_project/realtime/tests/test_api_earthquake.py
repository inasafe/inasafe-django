# coding=utf-8
import datetime
import logging
import os
import shutil

import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.gis.geos.point import Point
from django.core.files.base import File
from django.core.urlresolvers import reverse
from django.db import connections
from django.test.client import Client
from rest_framework import status
from rest_framework.test import APITestCase

from core.settings.utils import ABS_PATH
from realtime.app_settings import REST_GROUP
from realtime.models.earthquake import Earthquake, EarthquakeReport
from realtime.serializers.earthquake_serializer import EarthquakeSerializer, \
    EarthquakeReportSerializer
from realtime.serializers.pagination_serializer import \
    PageNumberPaginationSerializer
from realtime.tests.utilities import test_concurrently

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '20/06/15'

LOGGER = logging.getLogger(__name__)


class TestEarthquake(APITestCase):

    default_media_path = None

    def data_path(self, filename):
        return u'realtime/tests/data/earthquake/'+filename

    def setUp(self):
        if settings.TESTING:
            # move to media root for testing purposes
            self.default_media_path = settings.MEDIA_ROOT
            settings.MEDIA_ROOT = ABS_PATH('media_test')

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
        report.language = 'id'
        report.earthquake = earthquake
        if os.path.exists(self.data_path(report_pdf)):
            with open(self.data_path(report_pdf)) as pdf:
                report.report_pdf = File(pdf)
                report.save()
        if os.path.exists(self.data_path(report_png)):
            with open(self.data_path(report_png)) as png:
                report.report_image = File(png)
                report.save()
        if os.path.exists(self.data_path(report_thumb)):
            with open(self.data_path(report_thumb)) as thumb:
                report.report_thumbnail = File(thumb)
                report.save()

        # create test user
        User = get_user_model()
        self.user = User.objects.create_user(username='test',
                                             email='test@test.org',
                                             password='testsecret',
                                             location=Point(0, 0),
                                             email_updates=False)
        realtime_group = Group.objects.get(name=REST_GROUP)
        self.user.groups.add(realtime_group)
        self.user.save()
        self.client.login(email='test@test.org', password='testsecret')

    def tearDown(self):
        reports = EarthquakeReport.objects.all()
        for report in reports:
            report.delete()

        earthquakes = Earthquake.objects.all()
        for earthquake in earthquakes:
            earthquake.delete()

        if settings.TESTING:
            shutil.rmtree(settings.MEDIA_ROOT)
            settings.MEDIA_ROOT = self.default_media_path

        self.client.logout()
        realtime_group = Group.objects.get(name=REST_GROUP)
        self.user.groups.remove(realtime_group)
        self.user.save()
        self.user.delete()

    def test_earthquake_serializer(self):
        shake_dict = {
            'shake_id': u'20150619200629',
            'magnitude': 4.6,
            'time': u'2015-06-19T12:59:28Z',
            'depth': 10.0,
            'location': {
                u'type': u'Point',
                u'coordinates': [126.52, 4.16]
            },
            'location_description': u'Manado'
        }
        serializer = EarthquakeSerializer(data=shake_dict)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        earthquake = Earthquake.objects.get(shake_id=u'20150619200629')
        self.assertTrue(earthquake)
        serializer = EarthquakeSerializer(earthquake)
        for key, value in shake_dict.iteritems():
            self.assertEqual(serializer.data[key], value)
        earthquake.delete()

    def test_earthquake_report_serializer(self):
        report_dict = {
            'shake_id': u'20150619200628',
            'language': u'en',
            'report_pdf': File(
                open(
                    self.data_path(u'20150619200628-en.pdf'))),
            'report_image': File(
                open(
                    self.data_path(u'20150619200628-en.png'))),
            'report_thumbnail': File(
                open(
                    self.data_path(
                        u'20150619200628-thumb-en.png'))),
        }
        serializer = EarthquakeReportSerializer(data=report_dict)
        self.assertTrue(serializer.is_valid())
        earthquake = Earthquake.objects.get(shake_id=u'20150619200628')
        serializer.validated_data['earthquake'] = earthquake
        serializer.save()
        report = EarthquakeReport.objects.get(
            earthquake__shake_id=u'20150619200628',
            language=u'en'
        )
        self.assertTrue(report)
        serializer = EarthquakeReportSerializer(report)
        self.assertEqual(serializer.data['shake_id'], u'20150619200628')
        self.assertEqual(serializer.data['language'], u'en')

    def test_earthquake_list(self):
        response = self.client.get(reverse('realtime:earthquake_list'))
        expected_shake_id = '20150619200628'
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = PageNumberPaginationSerializer(
            serializer_class=EarthquakeSerializer, data=response.data)
        actual_results = serializer.results
        self.assertEqual(serializer.count, 1)
        self.assertEqual(actual_results[0]['shake_id'],
                         expected_shake_id)

    def test_earthquake_detail(self):
        kwargs = {'shake_id': '20150619200628'}
        response = self.client.get(reverse(
            'realtime:earthquake_detail',
            kwargs=kwargs))
        expected_earthquake = {
            'shake_id': u'20150619200628',
            'magnitude': 4.6,
            'time': u'2015-06-19T12:59:28Z',
            'depth': 10.0,
            'location': {
                u'type': u'Point',
                u'coordinates': [126.52, 4.16]
            },
            'location_description': u'Manado'
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        actual_earthquake = response.data
        for key, value in expected_earthquake.iteritems():
            self.assertEqual(actual_earthquake[key], value)

    def test_earthquake_list_post(self):
        shake_json = {
            'shake_id': u'20150619200629',
            'magnitude': 4.6,
            'time': u'2015-06-19T12:59:28Z',
            'depth': 10.0,
            'location': {
                u'type': u'Point',
                u'coordinates': [126.52, 4.16]
            },
            'location_description': u'Manado'
        }

        response = self.client.post(
            reverse('realtime:earthquake_list'),
            shake_json,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse('realtime:earthquake_list'))
        serializer = PageNumberPaginationSerializer(
            serializer_class=EarthquakeSerializer,
            data=response.data)
        self.assertEqual(serializer.count, 2)
        earthquake = Earthquake.objects.get(shake_id=u'20150619200629')
        serializer = EarthquakeSerializer(earthquake)
        for key, value in shake_json.iteritems():
            self.assertEqual(value, serializer.data[key])
        earthquake.delete()

    def test_earthquake_detail_put(self):
        shake_json = {
            'shake_id': u'20150619200629',
            'magnitude': 4.6,
            'time': u'2015-06-19T12:59:28Z',
            'depth': 10.0,
            'location': {
                u'type': u'Point',
                u'coordinates': [126.52, 4.16]
            },
            'location_description': u'Manado'
        }

        response = self.client.post(
            reverse('realtime:earthquake_list'),
            shake_json,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # change the data and put it using the same id
        shake_json['magnitude'] = 5.0

        response = self.client.put(
            reverse(
                'realtime:earthquake_detail',
                kwargs={'shake_id': shake_json['shake_id']}),
            shake_json,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check saved data
        earthquake = Earthquake.objects.get(shake_id=shake_json['shake_id'])
        self.assertEqual(earthquake.magnitude, shake_json['magnitude'])
        earthquake.delete()

    def test_earthquake_detail_delete(self):
        shake_json = {
            'shake_id': u'20150619200629',
            'magnitude': 4.6,
            'time': u'2015-06-19T12:59:28Z',
            'depth': 10.0,
            'location': {
                u'type': u'Point',
                u'coordinates': [126.52, 4.16]
            },
            'location_description': u'Manado'
        }

        response = self.client.post(
            reverse('realtime:earthquake_list'),
            shake_json,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # verify data is saved
        self.assertTrue(
            Earthquake.objects.get(shake_id=shake_json['shake_id']))

        # request delete
        response = self.client.delete(
            reverse(
                'realtime:earthquake_detail',
                kwargs={'shake_id': shake_json['shake_id']}
            ))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Earthquake.DoesNotExist):
            Earthquake.objects.get(shake_id=shake_json['shake_id'])

    def test_earthquake_report_list(self):
        response = self.client.get(
            reverse(
                'realtime:earthquake_report_list',
                kwargs={'shake_id': u'20150619200628'}
            ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_earthquake_report_list_post(self):
        report_multipart = {
            'language': u'en',
            'report_pdf': File(
                open(
                    self.data_path(u'20150619200628-en.pdf'))),
            'report_image': File(
                open(
                    self.data_path(u'20150619200628-en.png'))),
            'report_thumbnail': File(
                open(
                    self.data_path(
                        u'20150619200628-thumb-en.png'))),
        }

        response = self.client.post(
            reverse(
                'realtime:earthquake_report_list',
                kwargs={'shake_id': u'20150619200628'}
            ),
            report_multipart,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(
            reverse(
                'realtime:earthquake_report_list',
                kwargs={'shake_id': u'20150619200628'}
            ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = PageNumberPaginationSerializer(
            serializer_class=EarthquakeReportSerializer,
            data=response.data)
        self.assertEqual(serializer.count, 2)
        # delete data
        report = EarthquakeReport.objects.get(
            earthquake__shake_id=u'20150619200628',
            language='en')
        report.delete()

    def test_earthquake_report_detail(self):
        kwargs = {
            'shake_id': u'20150619200628',
            'language': u'id'
        }

        response = self.client.get(
            reverse(
                'realtime:earthquake_report_detail',
                kwargs=kwargs))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key, value in kwargs.iteritems():
            self.assertEqual(response.data[key], value)

    def test_earthquake_report_put(self):
        kwargs = {
            'shake_id': u'20150619200628',
            'language': u'id'
        }

        content = {
            'language': u'en'
        }

        response = self.client.put(
            reverse(
                'realtime:earthquake_report_detail',
                kwargs=kwargs),
            content,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check saved model
        report = EarthquakeReport.objects.get(
            earthquake__shake_id=kwargs['shake_id'],
            language=content['language'])
        self.assertTrue(report)
        self.assertEqual(report.language, u'en')
        # change it back
        report.language = u'id'
        report.save()

        # test change files
        content = {
            'report_pdf': File(open(self.data_path(u'20150619200628-en.pdf')))
        }

        response = self.client.put(
            reverse(
                'realtime:earthquake_report_detail',
                kwargs=kwargs),
            content,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report = EarthquakeReport.objects.get(
            earthquake__shake_id=kwargs['shake_id'],
            language=kwargs['language'])
        self.assertEqual(
            os.path.basename(report.report_pdf.name),
            u'20150619200628-en.pdf')
        # this should not change
        self.assertEqual(
            os.path.basename(report.report_image.name),
            u'20150619200628-id.png')

        # cleanup
        content = {
            'report_pdf': File(open(self.data_path(u'20150619200628-id.pdf')))
        }

        response = self.client.put(
            reverse(
                'realtime:earthquake_report_detail',
                kwargs=kwargs),
            content,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_earthquake_report_delete(self):
        report_multipart = {
            'language': u'en',
            'report_pdf': File(
                open(
                    self.data_path(u'20150619200628-en.pdf'))),
            'report_image': File(
                open(
                    self.data_path(u'20150619200628-en.png'))),
            'report_thumbnail': File(
                open(
                    self.data_path(
                        u'20150619200628-thumb-en.png'))),
        }

        response = self.client.post(
            reverse(
                'realtime:earthquake_report_list',
                kwargs={'shake_id': u'20150619200628'}
            ),
            report_multipart,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(
            reverse(
                'realtime:earthquake_report_list',
                kwargs={'shake_id': u'20150619200628'}
            ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = PageNumberPaginationSerializer(
            serializer_class=EarthquakeReportSerializer,
            data=response.data)
        self.assertEqual(serializer.count, 2)

        # delete using REST
        response = self.client.delete(
            reverse(
                'realtime:earthquake_report_detail',
                kwargs={
                    'shake_id': u'20150619200628',
                    'language': u'en'
                }
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # check saved objects
        reports = EarthquakeReport.objects.filter(
            earthquake__shake_id=u'20150619200628')
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].language, u'id')

    def xtest_earthquake_report_concurrency_post(self):
        """
        This is a test for concurrency post in EarthquakeReport GET method.

        This test currently not working because somehow the inner db
        connection in post_report has failed to connect.

        """
        report_multipart = {
            'language': u'en',
            'report_pdf': File(
                open(
                    self.data_path(u'20150619200628-en.pdf'))),
            'report_image': File(
                open(
                    self.data_path(u'20150619200628-en.png'))),
            'report_thumbnail': File(
                open(
                    self.data_path(
                        u'20150619200628-thumb-en.png'))),
        }

        @test_concurrently(15)
        def post_report(test_object):
            try:
                c = Client()
                login_ret = c.login(
                    email='test@test.org', password='testsecret')
                test_object.assertTrue(login_ret, 'Client is not logged in.')
                response = c.post(
                    reverse(
                        'realtime:earthquake_report_list',
                        kwargs={'shake_id': u'20150619200628'}
                    ),
                    report_multipart,
                    format='multipart'
                )
                test_object.assertEqual(
                    response.status_code, status.HTTP_200_OK)
            except Exception as e:
                for conn in connections.all():
                    conn.close()
                raise e

        post_report(self)

        req_args = {
            'shake_id': u'20150619200628',
            'language': u'en'
        }
        try:
            response = self.client.get(
                reverse(
                    'realtime:earthquake_report_detail',
                    kwargs=req_args
                ))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        finally:
            EarthquakeReport.objects.filter(
                earthquake__shake_id=req_args['shake_id'],
                language=req_args['language']
            ).delete()
