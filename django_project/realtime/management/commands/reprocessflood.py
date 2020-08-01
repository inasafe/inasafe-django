# coding=utf-8
from __future__ import print_function
from __future__ import division
from builtins import range
from past.utils import old_div
import datetime

import pytz
from django.core.management.base import BaseCommand

from realtime.models.flood import Flood

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/09/15'


class Command(BaseCommand):
    """Script to check indicator status. Can be executed via cronjob

    """
    help = 'Command to re-execute flood process on existing event id'

    def add_arguments(self, parser):
        parser.add_argument(
            'flood_event_ids',
            nargs='*',
            type=str)

        parser.add_argument(
            '--range',
            action='store_true',
        )

    def handle(self, *args, **options):
        using_range = options.get('range')
        flood_event_ids = options.get('flood_event_ids')
        if using_range and len(flood_event_ids) == 2:
            Command.regenerate_flood_from_range(
                flood_event_ids[0], flood_event_ids[1])

        if len(flood_event_ids) > 0 and not using_range:
            for event_id in flood_event_ids:
                print('Process using celery broker : {}'.format(event_id))
                flood = Flood.objects.get(event_id=event_id)
                flood.rerun_analysis()

        elif not using_range:
            floods = Flood.objects.all().order_by('-time')
            print(
                'Process using celery broker. '
                'Total number of events ({})'.format(len(floods)))
            for flood in floods:
                event_id = flood.event_id
                print('Process using celery broker : {}'.format(event_id))
                flood.rerun_analysis()

    @staticmethod
    def regenerate_flood_from_range(start_event_id, end_event_id):
        format_str = '%Y%m%d%H-6-rw'
        start_time = datetime.datetime.strptime(start_event_id, format_str)
        if not end_event_id == 'now':
            end_time = datetime.datetime.strptime(end_event_id, format_str)
        else:
            end_time = datetime.datetime.utcnow()
        # convert to UTC
        start_time = start_time.replace(tzinfo=pytz.UTC)
        end_time = end_time.replace(tzinfo=pytz.UTC)
        time_diff = end_time - start_time
        total_hours = int(old_div(time_diff.total_seconds(), 3600))
        total_events = 0
        for i in range(0, total_hours):
            hour_diff = datetime.timedelta(hours=i + 1)
            target_time = start_time + hour_diff
            event_id = target_time.strftime(format_str)
            try:
                print('Processing flood: {}'.format(event_id))
                flood = Flood.objects.get(event_id=event_id)
                flood.rerun_analysis()
                total_events += 1
            except Flood.DoesNotExist:
                pass

        print('Regenerate process done')
        print('Total processed events: {}'.format(total_events))
