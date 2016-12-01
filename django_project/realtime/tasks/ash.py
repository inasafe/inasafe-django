# coding=utf-8
from __future__ import absolute_import

import logging

from celery.result import AsyncResult

from core.celery_app import app
from realtime.tasks.realtime.celery_app import app as realtime_app
from realtime.app_settings import LOGGER_NAME
from realtime.models.ash import Ash

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '20/7/17'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(queue='inasafe-django')
def check_processing_task():
    for ash in Ash.objects.exclude(
            task_id__isnull=True).exclude(
            task_id__exact='').exclude(
            task_status__iexact='SUCCESS'):
        task_id = ash.task_id
        result = AsyncResult(id=task_id, app=realtime_app)
        ash.task_status = result.state
        ash.save()
