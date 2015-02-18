# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.conf import settings


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_view(self):
        response = self.client.get(reverse('front_end:home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['debug'], False)
        self.assertListEqual(
            [template.name for template in response.templates], [
                'main.html', u'base.html', u'pipeline/css.html',
                u'pipeline/css.html', u'pipeline/js.html', u'pipeline/js.html']
        )

    def test_home_view_no_googleanalytics(self):
        # specifically set DEBUG to True
        settings.DEBUG = True
        response = self.client.get(reverse('front_end:home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['debug'], True)
        self.assertTrue(response.content.find('GoogleAnalyticsObject') == -1)
        self.assertListEqual(
            [template.name for template in response.templates], [
                'main.html', u'base.html', u'pipeline/css.html',
                u'pipeline/css.html', u'pipeline/js.html', u'pipeline/js.html']
        )
