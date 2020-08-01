# coding=utf-8
from __future__ import print_function
from __future__ import division
from builtins import range
from past.utils import old_div
import datetime

import pytz
from django.core.management.base import BaseCommand
from realtime.tasks.flood import recalculate_impact_info

from realtime.models.flood import Flood

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/02/17'


class Command(BaseCommand):
    """Script to recalculate impact data.

    """
    help = (
        'Command to re-calculate total affected and boundary flooded in '
        'flood.')

    def handle(self, *args, **options):
        using_range = False
        if len(args) == 3:
            if args[0] == 'range':
                using_range = True
                Command.recalculate_flood_from_range(args[1], args[2])

        if len(args) > 0 and not using_range:
            for a in args:
                print('Process flood : %s' % a)
                flood = Flood.objects.get(event_id=a)
                try:
                    recalculate_impact_info(flood)
                except Exception as e:
                    print(e)

        elif not using_range:
            floods = Flood.objects.all().order_by('-time')
            print('Process flood (%s)' % len(floods))
            for flood in floods:
                try:
                    recalculate_impact_info(flood)
                except Exception as e:
                    print(e)

    @staticmethod
    def recalculate_flood_from_range(start_event_id, end_event_id):
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
        success = 0
        failed = 0
        for i in range(0, total_hours):
            hour_diff = datetime.timedelta(hours=i + 1)
            target_time = start_time + hour_diff
            event_id = target_time.strftime(format_str)
            try:
                print('Processing flood: %s' % event_id)
                flood = Flood.objects.get(event_id=event_id)
                recalculate_impact_info(flood)
                success += 1
            except Exception as e:
                failed += 1
                print(e)

        print('Recalculate process done')
        print('Success: %s. Failed: %s' % (success, failed))
