# coding=utf-8
import logging

from celery.canvas import chain
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from realtime.app_settings import LOGGER_NAME
from realtime.models.flood import Flood
from realtime.tasks.flood import process_hazard_layer, process_impact_layer

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/4/15'


LOGGER = logging.getLogger(LOGGER_NAME)


LOGGER.info('Signals registered')


@receiver(post_save, sender=Flood)
def flood_post_save(sender, **kwargs):
    """Extract impact layer of the flood"""
    try:
        instance = kwargs.get('instance')
        chain(
            process_hazard_layer.si(instance),
            process_impact_layer.si(instance))()
    except Exception as e:
        LOGGER.exception(e)
