# coding=utf-8
import logging

from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from realtime.app_settings import LOGGER_NAME
from realtime.models.flood import Flood, FloodEventBoundary, BoundaryAlias
from realtime.tasks.flood import generate_event_report, process_hazard_layer

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/4/15'


LOGGER = logging.getLogger(LOGGER_NAME)


LOGGER.info('Flood Signals registered')


@receiver(post_save, sender=Flood)
def flood_post_save(
        sender, instance, created=None, update_fields=None, **kwargs):
    """Extract impact layer of the flood"""
    try:
        fields = ['total_affected', 'boundary_flooded']
        update_fields = update_fields or []
        for field in fields:
            # if total_affected or boundary_flooded is updated,
            # do not recalculate
            if field in update_fields:
                break
        else:
            generate_event_report.delay(instance)
    except Exception as e:
        LOGGER.exception(e)

    # FIXME(IS): I use it to skip it in travis.
    if BoundaryAlias.objects.all():
        # Create FloodEventBoundary (to be shown in the map)
        if not FloodEventBoundary.objects.filter(flood=instance):
            process_hazard_layer.delay(instance)
    else:
        LOGGER.warning('No Boundary alias, not running process_hazard_layer.')
