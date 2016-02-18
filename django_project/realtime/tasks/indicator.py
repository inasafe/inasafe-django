# coding=utf-8
from __future__ import absolute_import

import logging
from datetime import datetime

import os
import pytz
import time

from realtime.celery_app import app

from realtime.app_settings import LOGGER_NAME
from realtime.helpers.realtime_broker_indicator import RealtimeBrokerIndicator
from realtime.tasks.realtime.generic import check_broker_connection

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/17/16'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(queue='inasafe-django')
def log_error(task_id):
    result = app.AsyncResult(task_id)
    result.get(propagate=False)  # make sure result written.
    with open(os.path.join('/var/errors', task_id), 'a') as fh:
        fh.write('--\n\n{0} {1} {2}'.format(task_id, result.result, result.traceback))


@app.task(queue='inasafe-django')
def update_indicator(check_broker_retval):
    if check_broker_retval:
        indicator = RealtimeBrokerIndicator()
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        indicator.value = now


@app.task(queue='inasafe-django')
def check_realtime_broker():
    res = check_broker_connection.delay()
    # wait to sync result
    while not res.ready():
        time.sleep(5)
    if res.successful():
        update_indicator.delay(res.result)

