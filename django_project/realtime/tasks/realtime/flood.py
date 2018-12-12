# coding=utf-8
import logging

import pytz

from realtime.app_settings import LOGGER_NAME
from realtime.tasks.realtime.celery_app import app

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/16/16'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(
    name='realtime.tasks.flood.process_flood', queue='inasafe-realtime')
def process_flood(
        flood_id=None, time_zone=pytz.timezone('Asia/Jakarta'),
        data_source='petabencana', data_source_args=None):
    """Celery task for flood hazard.
    :param flood_id: (Optional) if provided, will use the value for
        id
    :type flood_id: str

    :param time_zone: Timezone of Flood Hazard
    :type time_zone: pytz.tzinfo.DstTzInfo

    :param data_source: Data Source type
    :type data_source: str

    :param data_source_args: (Optional).Supply this for Data Source API method
    :type data_source_args: dict
    """
    LOGGER.info('proxy tasks')
    pass
