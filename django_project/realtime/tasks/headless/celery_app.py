# coding=utf-8
"""Celery app for InaSAFE headless."""
from __future__ import absolute_import
from celery import Celery

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


app = Celery('headless.tasks')
app.config_from_object('realtime.tasks.headless.celeryconfig')
