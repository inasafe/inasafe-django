# coding=utf-8
"""Model class for ash realtime."""
import json
import os

import pytz
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

__author__ = 'myarjunar'
__project_name__ = 'inasafe-django'
__filename__ = 'impact'
__date__ = '4/18/18'
__copyright__ = 'myarjunar@gmail.com'


class Impact(models.Model):
    """Impact model."""
    class Meta:
        """Meta class."""
        app_label = 'realtime'
        verbose_name_plural = 'Impact'
