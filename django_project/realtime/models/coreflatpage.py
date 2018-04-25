# coding=utf-8

from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.contrib.gis.db import models

from realtime.app_settings import (
    FLATPAGE_SYSTEM_CATEGORY,
    FLATPAGE_SYSTEM_SLUG_IDS, OTHER_PAGE_SYSTEM_CATEGORY)

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'


class CoreFlatPage(FlatPage):
    """Custom Flatpage with grouping"""

    group = models.CharField(
        verbose_name='Group of FlatPage',
        help_text='Help categorizes this flat page in a group',
        max_length=100,
        blank=True)
    system_category = models.CharField(
        verbose_name='System category used for internal CMS',
        help_text='Help categorizes this flat page for internal CMS',
        max_length=30,
        null=True,
        blank=True,
        choices=FLATPAGE_SYSTEM_CATEGORY,
        default=OTHER_PAGE_SYSTEM_CATEGORY)
    slug_id = models.CharField(
        verbose_name='Slug ID used as reference for internal CMS',
        help_text='These slug ID will contains predetermined values',
        max_length=30,
        choices=FLATPAGE_SYSTEM_SLUG_IDS,
        null=True,
        blank=True)
    order = models.IntegerField(
        verbose_name='Order of the page',
        help_text='Help manage the order of the page as shown in the nav bar '
                  'menu. Smaller means on top. Pages shown in navbar sorted '
                  'by decreasing order value.',
        default=0)
    language = models.CharField(
        verbose_name='Language code of the page',
        help_text='Help tag the language of the code',
        max_length=10,
        null=True,
        blank=True,
        choices=settings.LANGUAGES,
        default='en')
