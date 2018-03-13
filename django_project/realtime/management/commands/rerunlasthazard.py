# coding=utf-8
import logging

from django.core.management.base import BaseCommand

from realtime.models.ash import Ash
from realtime.models.earthquake import Earthquake
from realtime.models.flood import Flood

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'


LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """Script to check indicator status. Can be executed via cronjob

    """
    help = 'Command to re-execute analysis and report generation for ' \
           'last hazard'

    def handle(self, *args, **options):

        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.INFO)

        # Regenerate Earthquake
        try:
            LOGGER.info('Regenerate Last EQ')
            event = Earthquake.objects.order_by('id').last()
            LOGGER.info('Shake ID: {0}'.format(event.shake_id))
            LOGGER.info('Source Type: {0}'.format(event.source_type))
            event.rerun_analysis()
            LOGGER.info('Delegated analysis rerun')

        except BaseException as e:
            LOGGER.exception(e)

        # Regenerate Flood
        try:
            LOGGER.info('Regenerate Last Flood')
            event = Flood.objects.order_by('id').last()
            LOGGER.info('Flood ID: {0}'.format(event.event_id))
            event.rerun_analysis()
            LOGGER.info('Delegated analysis rerun')

        except BaseException as e:
            LOGGER.exception(e)

        # Regenerate Ash
        try:
            LOGGER.info('Regenerate Last Ash')
            event = Ash.objects.order_by('id').last()
            LOGGER.info('Ash ID: {0}'.format(event.event_id_formatted))
            event.rerun_analysis()
            LOGGER.info('Delegated analysis rerun')

        except BaseException as e:
            LOGGER.exception(e)

        LOGGER.info('Command finished.')
