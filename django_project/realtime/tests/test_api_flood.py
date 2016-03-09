# coding=utf-8
import datetime
import filecmp
import logging
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.gis.geos.point import Point
from django.core.files.base import File
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.settings.utils import ABS_PATH
from realtime.app_settings import REST_GROUP
from realtime.models.flood import Flood, FloodReport
from realtime.serializers.flood_serializer import FloodSerializer, \
    FloodReportSerializer
from realtime.serializers.pagination_serializer import \
    PageNumberPaginationSerializer
from realtime.tests.utilities import assertEqualDictionaryWithFiles

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '11/30/15'


LOGGER = logging.getLogger(__name__)


class TestFlood(APITestCase):

    default_media_path = None

    def data_path(self, filename):
        return u'realtime/tests/data/flood/'+filename

    def assertEqualDictionaryWithFiles(self, dict_value, dict_control):
        assertEqualDictionaryWithFiles(self, dict_value, dict_control)

    def setUp(self):
        if settings.TESTING:
            # move to media root for testing purposes
            self.default_media_path = settings.MEDIA_ROOT
            settings.MEDIA_ROOT = ABS_PATH('media_test')

        flood = Flood.objects.create(
            event_id=u'2015112518-3-rw',
            time=datetime.datetime(
                2015, 11, 25, 18, 0, 0
            ),
            interval=3,
            source=u'Peta Jakarta',
            region=u'Jakarta',
            hazard_layer=File(open(
                self.data_path('hazard.zip')
            ))
        )

        FloodReport.objects.create(
            flood=flood,
            language='en',
            impact_report=File(open(
                self.data_path('impact-table-en.pdf')
            )),
            impact_map=File(open(
                self.data_path('impact-map-en.pdf')
            )),
        )

        # create test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username='test',
            email='test@test.org',
            password='testsecret',
            location=Point(0, 0),
            email_updates=False)
        realtime_group = Group.objects.get(name=REST_GROUP)
        self.user.groups.add(realtime_group)
        self.user.save()
        self.client.login(email='test@test.org', password='testsecret')

    def tearDown(self):
        for f in FloodReport.objects.all():
            f.delete()

        for f in Flood.objects.all():
            f.delete()

    def test_flood_serializer(self):
        """Test for Flood Serializer"""
        flood_dict = {
            'event_id': u'2015112518-6-rw',
            'time': u'2015-11-25T18:00:00Z',
            'interval': 6,
            'source': u'Peta Jakarta',
            'region': u'Jakarta',
            'hazard_layer': File(open(
                self.data_path('hazard.zip')
            ))
        }

        serializer = FloodSerializer(data=flood_dict)
        # Test serializing from dict to model
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        flood = Flood.objects.get(event_id=flood_dict['event_id'])
        # Test that serializer saves dict to model
        self.assertTrue(flood)
        serializer = FloodSerializer(flood)
        self.assertEqualDictionaryWithFiles(serializer.data, flood_dict)
        flood.delete()

    def test_flood_report_serializer(self):
        """Test for Report Serializer"""
        report_dict = {
            'event_id': u'2015112518-3-rw',
            'language': u'id',
            'impact_report': File(
                open(self.data_path('impact-table-id.pdf'))
            ),
            'impact_map': File(
                open(self.data_path('impact-map-id.pdf'))
            )
        }
        serializer = FloodReportSerializer(data=report_dict)
        # Test that Serializer from dict to model works
        self.assertTrue(serializer.is_valid())
        flood = Flood.objects.get(event_id=u'2015112518-3-rw')
        serializer.validated_data['flood'] = flood
        serializer.save()

        try:
            report = FloodReport.objects.get(
                flood__event_id=u'2015112518-3-rw',
                language=u'id'
            )
        except FloodReport.DoesNotExist:
            pass
        # Test that report exists
        self.assertTrue(report)

        flood = Flood.objects.get(event_id=u'2015112518-3-rw')
        # Test that flood report is in the Floods model reports member
        # property
        self.assertIn(report, flood.reports.all())

        serializer = FloodReportSerializer(report)
        # Test member of the serialized model equals dict value
        self.assertEqualDictionaryWithFiles(serializer.data, report_dict)

    def test_flood_list(self):
        response = self.client.get(reverse('realtime:flood_list'))
        expected_event_id = '2015112518-3-rw'
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = PageNumberPaginationSerializer(
            serializer_class=FloodSerializer,
            data=response.data
        )
        actual_results = serializer.results
        self.assertEqual(serializer.count, 1)
        self.assertEqual(actual_results[0]['event_id'], expected_event_id)

    def test_flood_detail(self):
        kwargs = {'event_id': '2015112518-3-rw'}
        response = self.client.get(reverse(
            'realtime:flood_detail',
            kwargs=kwargs
        ))
        expected_flood = {
            'event_id': u'2015112518-3-rw',
            'time': u'2015-11-25T18:00:00Z',
            'interval': 3,
            'source': u'Peta Jakarta',
            'region': u'Jakarta',
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        actual_flood = response.data
        self.assertEqualDictionaryWithFiles(actual_flood, expected_flood)

    def test_flood_post(self):
        flood_json = {
            'event_id': u'2015112518-6-rw',
            'time': u'2015-11-25T18:00:00Z',
            'interval': 3,
            'source': u'Peta Jakarta',
            'region': u'Jakarta',
            'hazard_layer': File(
                open(self.data_path('hazard.zip'))
            )
        }

        response = self.client.post(
            reverse('realtime:flood_list'),
            flood_json,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse('realtime:flood_list'))
        serializer = PageNumberPaginationSerializer(
            serializer_class=FloodSerializer,
            data=response.data
        )
        self.assertEqual(serializer.count, 2)
        flood = Flood.objects.get(event_id=flood_json['event_id'])
        serializer = FloodSerializer(flood)
        self.assertEqualDictionaryWithFiles(serializer.data, flood_json)

        flood.delete()

    def test_flood_detail_put(self):
        flood_json = {
            'event_id': u'2015112518-6-rw',
            'time': u'2015-11-25T18:00:00Z',
            'interval': 3,
            'source': u'Peta Jakarta',
            'region': u'Jakarta',
        }

        response = self.client.post(
            reverse('realtime:flood_list'),
            flood_json,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # put file data using multipart
        flood_json['hazard_layer'] = File(
            open(self.data_path('hazard.zip')))

        response = self.client.put(
            reverse(
                'realtime:flood_detail',
                kwargs={
                    'event_id': flood_json['event_id']
                }),
            flood_json,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check saved data
        response = self.client.get(
            reverse(
                'realtime:flood_detail',
                kwargs={
                    'event_id': flood_json['event_id']
                }
            )
        )

        flood = Flood.objects.get(event_id=flood_json['event_id'])

        self.assertTrue(
            filecmp.cmp(
                os.path.join(
                    settings.MEDIA_ROOT,
                    flood.hazard_layer.name
                ),
                self.data_path('hazard.zip')
            )
        )
        flood.delete()

    def test_flood_detail_delete(self):
        flood_json = {
            'event_id': u'2015112518-6-rw',
            'time': u'2015-11-25T18:00:00Z',
            'interval': 3,
            'source': u'Peta Jakarta',
            'region': u'Jakarta',
            'hazard_layer': File(
                open(self.data_path('hazard.zip'))
            )
        }

        # post the data
        response = self.client.post(
            reverse('realtime:flood_list'),
            flood_json,
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        try:
            flood = Flood.objects.get(event_id=flood_json['event_id'])
        except Flood.DoesNotExist:
            pass

        # check data exists
        self.assertTrue(flood)
        hazard_layer_file = os.path.join(
            settings.MEDIA_ROOT,
            flood.hazard_layer.name
        )
        self.assertTrue(os.path.exists(hazard_layer_file))

        # delete object via rest

        response = self.client.delete(
            reverse(
                'realtime:flood_detail',
                kwargs={'event_id': flood_json['event_id']}
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Flood.DoesNotExist):
            Flood.objects.get(event_id=flood_json['event_id'])

        self.assertFalse(os.path.exists(hazard_layer_file))

    def test_flood_report_list(self):
        response = self.client.get(
            reverse(
                'realtime:flood_report_list',
                kwargs={'event_id': u'2015112518-3-rw'}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_flood_report_post(self):
        report_dict = {
            'event_id': u'2015112518-3-rw',
            'language': u'id',
            'impact_report': File(
                open(self.data_path('impact-table-id.pdf'))
            ),
            'impact_map': File(
                open(self.data_path('impact-map-id.pdf'))
            )
        }

        response = self.client.post(
            reverse(
                'realtime:flood_report_list',
                kwargs={'event_id': report_dict['event_id']}
            ),
            report_dict,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse('realtime:flood_report_list'))

        # Test the json returns
        self.assertEqual(response.data['count'], 2)
        self.assertEqualDictionaryWithFiles(
            response.data['results'][0], report_dict)

        # Test using serializer
        serializer = PageNumberPaginationSerializer(
            serializer_class=FloodReportSerializer,
            data=response.data)
        self.assertEqual(serializer.count, 2)
        self.assertEqualDictionaryWithFiles(serializer.results[0], report_dict)
        report = FloodReport.objects.get(
            flood__event_id=report_dict['event_id'],
            language=u'id')
        serializer = FloodReportSerializer(report)
        self.assertEqualDictionaryWithFiles(serializer.data, report_dict)

        report.delete()

    def test_flood_report_detail(self):
        report_dict = {
            'event_id': u'2015112518-3-rw',
            'language': u'en',
            'impact_report': File(
                open(self.data_path('impact-table-en.pdf'))
            ),
            'impact_map': File(
                open(self.data_path('impact-map-en.pdf'))
            )
        }

        response = self.client.get(
            reverse(
                'realtime:flood_report_detail',
                kwargs={
                    'event_id': report_dict['event_id'],
                    'language': report_dict['language']
                }
            ))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqualDictionaryWithFiles(response.data, report_dict)

    def test_flood_report_put(self):
        report_dict = {
            'event_id': u'2015112518-3-rw',
            'language': u'id'
        }

        response = self.client.post(
            reverse(
                'realtime:flood_report_list',
                kwargs={'event_id': report_dict['event_id']}
            ),
            report_dict,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(
            reverse(
                'realtime:flood_report_detail',
                kwargs={
                    'event_id': report_dict['event_id'],
                    'language': report_dict['language']
                }
            ))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that impact map and report is empty
        self.assertFalse(response.data.get('impact_map'))
        self.assertFalse(response.data.get('impact_report'))

        # Update data using put
        report_dict['impact_report'] = File(
            open(self.data_path('impact-table-id.pdf'))
        )
        report_dict['impact_map'] = File(
            open(self.data_path('impact-map-id.pdf'))
        )

        response = self.client.put(
            reverse(
                'realtime:flood_report_detail',
                kwargs={
                    'event_id': report_dict['event_id'],
                    'language': report_dict['language']
                }
            ),
            report_dict,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            reverse(
                'realtime:flood_report_detail',
                kwargs={
                    'event_id': report_dict['event_id'],
                    'language': report_dict['language']
                }
            ))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that impact map and report is NOT empty
        self.assertTrue(response.data.get('impact_map'))
        self.assertTrue(response.data.get('impact_report'))
        # and correct
        self.assertEqualDictionaryWithFiles(response.data, report_dict)

        # Now change some values
        report_dict['impact_map'] = File(
            open(self.data_path('impact-map-en.pdf')))

        report_dict.pop('impact_report')

        response = self.client.put(
            reverse(
                'realtime:flood_report_detail',
                kwargs={
                    'event_id': report_dict['event_id'],
                    'language': report_dict['language']
                }
            ),
            report_dict,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            reverse(
                'realtime:flood_report_detail',
                kwargs={
                    'event_id': report_dict['event_id'],
                    'language': report_dict['language']
                }
            ))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the change is reflected and correct
        self.assertEqualDictionaryWithFiles(response.data, report_dict)

        report = FloodReport.objects.get(
            flood__event_id=report_dict['event_id'],
            language=report_dict['language'])
        report.delete()

    def test_flood_report_delete(self):
        report_dict = {
            'event_id': u'2015112518-3-rw',
            'language': u'id',
            'impact_report': File(
                open(self.data_path('impact-table-id.pdf'))
            ),
            'impact_map': File(
                open(self.data_path('impact-map-id.pdf'))
            )
        }

        response = self.client.post(
            reverse(
                'realtime:flood_report_list',
                kwargs={'event_id': report_dict['event_id']}
            ),
            report_dict,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(
            reverse(
                'realtime:flood_report_detail',
                kwargs={
                    'event_id': report_dict['event_id'],
                    'language': report_dict['language']
                }
            ))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check that post succes
        report = FloodReport.objects.get(
            flood__event_id=report_dict['event_id'],
            language=report_dict['language']
        )
        self.assertTrue(report)

        serializer = FloodReportSerializer(report)

        # Check content the same
        self.assertEqualDictionaryWithFiles(serializer.data, report_dict)

        # delete using REST

        response = self.client.delete(
            reverse(
                'realtime:flood_report_detail',
                kwargs={
                    'event_id': report_dict['event_id'],
                    'language': report_dict['language']
                }
            ))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check report doesn't exists anymore
        with self.assertRaises(FloodReport.DoesNotExist):
            FloodReport.objects.get(
                flood__event_id=report_dict['event_id'],
                language=report_dict['language']
            )

    def test_flood_save(self):
        f = Flood.objects.all()[0]
        f.save()
