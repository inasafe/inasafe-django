# coding=utf-8
import logging

from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from realtime.app_settings import LOGGER_NAME, ANALYSIS_LANGUAGES
from realtime.models.flood import Flood
from realtime.tasks.flood import generate_event_report
from realtime.tasks.geonode import push_hazard_to_geonode

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/4/15'


LOGGER = logging.getLogger(LOGGER_NAME)


LOGGER.info('Flood Signals registered')


@receiver(post_save)
def flood_post_save(
        sender, instance, created=None, update_fields=None, **kwargs):
    """Extract impact layer of the flood"""

    if not issubclass(sender, Flood):
        return

    try:
        if instance.analysis_flag:
            for lang in ANALYSIS_LANGUAGES:
                generate_event_report.delay(instance, locale=lang)
        if instance.analysis_flag:
            push_hazard_to_geonode.delay(instance)
    except Exception as e:
        LOGGER.exception(e)
