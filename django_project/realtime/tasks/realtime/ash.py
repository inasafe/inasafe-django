# coding=utf-8
import logging

from realtime.app_settings import LOGGER_NAME
from realtime.tasks.realtime.celery_app import app

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '7/20/16'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(
    name='realtime.tasks.ash.process_ash',
    queue='inasafe-realtime')
def process_ash(
        event_time=None,
        volcano_name=None,
        volcano_location=None,
        eruption_height=None,
        vent_height=None,
        region=None,
        alert_level=None,
        hazard_url=None):
    LOGGER.info('proxy tasks')
    pass
