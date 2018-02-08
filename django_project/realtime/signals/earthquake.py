# coding=utf-8
import logging

from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from realtime.app_settings import LOGGER_NAME
from realtime.models.ash import Ash
from realtime.tasks.earthquake import generate_event_report

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '7/18/16'


LOGGER = logging.getLogger(LOGGER_NAME)


LOGGER.info('Earthquake Signals registered')


@receiver(post_save, sender=Ash)
def earthquake_post_save(sender, instance, **kwargs):
    """Extract impact layer of the flood"""
    try:
        LOGGER.info('Sending task earthquake processing.')
        generate_event_report.delay(instance)
    except BaseException:
        pass
