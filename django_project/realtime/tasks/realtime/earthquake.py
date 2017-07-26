# coding=utf-8
import logging

from realtime.app_settings import LOGGER_NAME
from realtime.tasks.realtime.celery_app import app

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '3/8/16'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(
    name='realtime.tasks.earthquake.process_shake',
    queue='inasafe-realtime')
def process_shake(event_id=None):
    LOGGER.info('proxy tasks')
    pass


@app.task(
    name='realtime.tasks.earthquake.check_event_exists',
    queue='inasafe-realtime')
def check_event_exists(event_id=None):
    LOGGER.info('proxy tasks')
    pass
