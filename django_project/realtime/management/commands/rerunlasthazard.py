# coding=utf-8
from __future__ import print_function
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

        # Regenerate Earthquake
        try:
            print('Regenerate Last EQ')
            event = Earthquake.objects.order_by('id').last()
            print('Shake ID: {0}'.format(event.shake_id))
            print('Source Type: {0}'.format(event.source_type))
            event.rerun_analysis()
            print('Delegated analysis rerun')

        except BaseException as e:
            LOGGER.exception(e)

        # Regenerate Flood
        try:
            print('Regenerate Last Flood')
            event = Flood.objects.order_by('id').last()
            print('Flood ID: {0}'.format(event.event_id))
            event.rerun_analysis()
            print('Delegated analysis rerun')

        except BaseException as e:
            LOGGER.exception(e)

        # Regenerate Ash
        try:
            print('Regenerate Last Ash')
            event = Ash.objects.order_by('id').last()
            print('Ash ID: {0}'.format(event.event_id_formatted))
            event.rerun_analysis()
            print('Delegated analysis rerun')

        except BaseException as e:
            LOGGER.exception(e)

        print('Command finished.')
