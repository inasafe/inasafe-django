# coding=utf-8

from django.contrib.flatpages.models import FlatPage
from django.contrib.gis.db import models

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'


class CoreFlatPage(FlatPage):
    """Custom Flatpage with grouping"""

    group = models.CharField(
        verbose_name='Group of FlatPage',
        help_text='Help categorizes this flat page in a group',
        max_length=100,
        blank=True)
