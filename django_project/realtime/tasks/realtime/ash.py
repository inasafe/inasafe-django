# coding=utf-8
import logging

from realtime.app_settings import LOGGER_NAME
from realtime.tasks.realtime.celery_app import app

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '7/20/16'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(
    name='realtime.tasks.flood.process_ash', queue='inasafe-realtime')
def process_ash(
        ash_file_path, volcano_name, region,
        latitude, longitude, alert_level,
        event_time, eruption_height, vent_height, forecast_duration):
    """Celery tasks to process ash hazard.

    :param ash_file_path: File path to ash layer
    :type ash_file_path: str

    :param volcano_name: The volcano name
    :type volcano_name: str

    :param region: The region where the volcano located
    :type region: str

    :param latitude: Latitude number in EPSG:4326
    :type latitude: float

    :param longitude: Longitude number in EPSG:4326
    :type longitude: float

    :param alert_level: Alert level string. Alailable value:
        Normal, Warning, Advisory, Watch
    :type alert_level: str

    :param event_time: Event time of Ash with timezone
    :type event_time: datetime.datetime

    :param eruption_height: Eruption height calculated from volcano height
        / vent height
    :type eruption_height: float

    :param vent_height: Height of volcano / Height of vent
    :type vent_height: float

    :param forecast_duration: Forecast duration of model in days
    :type forecast_duration: float
    """
    LOGGER.info('proxy tasks')
    pass
