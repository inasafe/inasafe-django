# coding=utf-8
import logging

from realtime.app_settings import LOGGER_NAME
from realtime.tasks.realtime.celery_app import app

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/17/16'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(
    name='realtime.tasks.generic.check_broker_connection',
    queue='inasafe-realtime')
def check_broker_connection():
    """Only returns true if broker is connected

    :return: True
    """
    LOGGER.info('proxy tasks')
    return True
