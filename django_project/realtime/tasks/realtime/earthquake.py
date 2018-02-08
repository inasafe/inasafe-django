# coding=utf-8
import logging

from realtime.app_settings import LOGGER_NAME
from realtime.tasks.realtime.celery_app import app

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '3/8/16'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(
    name='realtime.tasks.earthquake.process_shake', queue='inasafe-realtime')
def process_shake(event_id=None, grid_file=None, source_type='initial'):
    """Celery task for shake hazard.

    :param event_id: Event id of shake
    :type event_id: str

    :param grid_file: Grid file location relative to shakemap working
        directory
    :type grid_file: str

    :param source_type: The type of grid source. Available value:
        initial, post-processed
    :type source_type: str

    :return:
    """
    LOGGER.info('proxy tasks')
    pass
