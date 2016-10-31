# coding=utf-8
import logging

import pytz
from urlparse import urljoin
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from realtime.app_settings import LOGGER_NAME
from realtime.models.ash import Ash
from realtime.tasks.realtime.ash import process_ash

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '7/18/16'


LOGGER = logging.getLogger(LOGGER_NAME)


LOGGER.info('Signals registered')


@receiver(post_save, sender=Ash)
def ash_post_save(sender, **kwargs):
    """Extract impact layer of the flood"""
    try:
        instance = kwargs.get('instance')
        if isinstance(instance, Ash):
            # Only do processing when it is a new ash
            if instance.task_status and not instance.task_status == 'None':
                return

            if instance.event_time.tzinfo:
                event_time = instance.event_time
            else:
                event_time = instance.event_time.replace(tzinfo=pytz.utc)

            location = [
                instance.volcano.location[0],
                instance.volcano.location[1]
            ]
            hazard_url = urljoin(
                settings.SITE_DOMAIN_NAME,
                instance.hazard_file.url)
            LOGGER.info('Sending task ash processing.')
            result = process_ash.delay(
                event_time=event_time,
                volcano_name=instance.volcano.volcano_name,
                volcano_location=location,
                eruption_height=instance.eruption_height,
                region=instance.volcano.province,
                alert_level=instance.alert_level,
                hazard_url=hazard_url)
            instance.task_id = result.id
            instance.task_status = 'PENDING'
            instance.save()
    except:
        pass
