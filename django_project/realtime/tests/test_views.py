# coding=utf-8

from django import test
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.gis.geos import Point
from django.core.urlresolvers import reverse
from requests import status_codes

from realtime.app_settings import FLATPAGE_SYSTEM_SLUG_IDS, \
    LANDING_PAGE_SYSTEM_CATEGORY
from realtime.models.coreflatpage import CoreFlatPage


class TestViews(test.TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='test',
                                             email='test@test.org',
                                             password='testsecret',
                                             location=Point(0, 0),
                                             email_updates=False)
        permissions = Permission.objects.filter(
            codename__in=[
                'change_coreflatpage',
                'add_coreflatpage',
                'delete_coreflatpage'])
        for p in permissions:
            self.user.user_permissions.add(p)
        self.user.is_admin = True
        self.user.save()
        self.client.login(email='test@test.org', password='testsecret')

    def test_edit_landing_page(self):
        """Test edit landing page text using shortcut."""

        lang = 'id'
        for slug_id, _ in FLATPAGE_SYSTEM_SLUG_IDS:
            edit_page_url = reverse(
                'realtime:flatpage_edit',
                kwargs={
                    'slug_id': slug_id,
                    'system_category': LANDING_PAGE_SYSTEM_CATEGORY,
                    'language': lang
                })

            response = self.client.get(edit_page_url)
            self.assertEqual(response.status_code, status_codes.codes.found)

            page = CoreFlatPage.objects.get(
                slug_id=slug_id,
                system_category=LANDING_PAGE_SYSTEM_CATEGORY,
                language=lang)

            location_header = response['location']
            flatpage_url = reverse(
                'admin:realtime_coreflatpage_change', args=(page.id, ))

            self.assertTrue(location_header.endswith(flatpage_url))

            response = self.client.get(flatpage_url)

            self.assertEqual(response.status_code, status_codes.codes.ok)

            self.assertTrue(page)

        landing_pages = CoreFlatPage.objects.filter(
            system_category=LANDING_PAGE_SYSTEM_CATEGORY)
        self.assertEqual(landing_pages.count(), len(FLATPAGE_SYSTEM_SLUG_IDS))
