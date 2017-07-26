# coding=utf-8
import logging

from realtime.app_settings import LOGGER_NAME
from realtime.tasks.realtime.celery_app import app

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/16/16'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(
    name='realtime.tasks.flood.process_flood',
    queue='inasafe-realtime')
def process_flood(event_folder=None):
    LOGGER.info('proxy tasks')
    pass
