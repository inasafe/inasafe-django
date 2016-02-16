# coding=utf-8
import logging

from realtime.tasks.realtime.celery_app import app

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/16/16'


LOGGER = logging.getLogger(__file__)


@app.task(
    name='realtime.tasks.flood.process_flood',
    queue='inasafe-realtime')
def process_flood():
    LOGGER.info('proxy tasks')
    pass
