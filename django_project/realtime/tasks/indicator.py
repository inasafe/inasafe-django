# coding=utf-8
from __future__ import absolute_import

import logging
import os
from datetime import datetime

import pytz
from celery.result import allow_join_result

from core.celery_app import app
from realtime.app_settings import LOGGER_NAME
from realtime.helpers.realtime_broker_indicator import RealtimeBrokerIndicator
from realtime.scripts.check_indicators import check_indicator_status
from realtime.tasks.realtime.generic import check_broker_connection

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/17/16'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(queue='inasafe-django-indicator')
def log_error(task_id):
    result = app.AsyncResult(task_id)
    result.get(propagate=False)  # make sure result written.
    with open(os.path.join('/var/errors', task_id), 'a') as fh:
        fh.write(
            '--\n\n{0} {1} {2}'.format(
                task_id, result.result, result.traceback))


@app.task(queue='inasafe-django-indicator')
def update_indicator(check_broker_retval):
    if check_broker_retval:
        indicator = RealtimeBrokerIndicator()
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        indicator.value = now
        return True
    return False


@app.task(queue='inasafe-django-indicator')
def check_realtime_broker():
    res = check_broker_connection.delay()
    # wait to sync result
    try:
        with allow_join_result():
            update_indicator.delay(res.get())
            return res.get()
    except BaseException as e:
        LOGGER.exception(e)
    return False


@app.task(queue='inasafe-django-indicator')
def notify_indicator_status():
    check_indicator_status()
