# coding=utf-8
from __future__ import absolute_import

import logging
import shutil
from tempfile import mkdtemp

import os
import pytz
from celery.result import AsyncResult

from core.celery_app import app
from realtime.app_settings import LOGGER_NAME, REALTIME_HAZARD_DROP
from realtime.models.ash import Ash
from realtime.tasks.realtime.ash import process_ash
from realtime.tasks.realtime.celery_app import app as realtime_app

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '20/7/17'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(queue='inasafe-django')
def check_processing_task():
    for ash in Ash.objects.exclude(
            task_id__isnull=True).exclude(
            task_id__exact='').exclude(
            task_status__iexact='SUCCESS'):
        task_id = ash.task_id
        result = AsyncResult(id=task_id, app=realtime_app)
        ash.task_status = result.state
        ash.save()


@app.task(queue='inasafe-django')
def generate_event_report(ash_event):
    """Generate Ash Report

    :param ash_event: Ash event instance
    :type ash_event: Ash
    :return:
    """
    ash_event.use_timezone()

    if ash_event.event_time.tzinfo:
        event_time = ash_event.event_time
    else:
        event_time = ash_event.event_time.replace(tzinfo=pytz.utc)

    if not ash_event.hazard_layer_exists:

        # For ash realtime we need to make sure hazard file is processed.
        # Because the hazard raw data comes from user upload

        # copy hazard data realtime location
        hazard_drop_path = mkdtemp(dir=REALTIME_HAZARD_DROP)
        hazard_drop_path = os.path.join(
            hazard_drop_path, os.path.basename(ash_event.hazard_file.path))
        shutil.copy(ash_event.hazard_file.path, hazard_drop_path)

        LOGGER.info('Sending task ash hazard processing.')
        result = process_ash.delay(
            ash_file_path=hazard_drop_path,
            volcano_name=ash_event.volcano.volcano_name,
            region=ash_event.volcano.province,
            latitude=ash_event.volcano.location[1],
            longitude=ash_event.volcano.location[0],
            alert_level=ash_event.alert_level,
            event_time=event_time,
            eruption_height=ash_event.eruption_height,
            vent_height=ash_event.volcano.elevation,
            forecast_duration=ash_event.forecast_duration)

        task_result = result.get()

        success = task_result.get('success')
        hazard_path = task_result.get('hazard_path')

        if not success:
            raise Exception('Error Generating Hazard file.')

        ash_event.hazard_path = hazard_path
        Ash.objects.filter(id=ash_event.id).update(hazard_path=hazard_path)

    # TODO: Generate Ash report

    # TODO: Save Ash products to databases
