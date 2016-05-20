# coding=utf-8
import datetime

import pytz
from django.core.management.base import BaseCommand

from realtime.models.flood import Flood
from realtime.tasks.realtime.flood import process_flood

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/09/15'


class Command(BaseCommand):
    """Script to check indicator status. Can be executed via cronjob

    """
    help = 'Command to re-execute flood process on existing event id'

    def handle(self, *args, **options):
        using_range = False
        if len(args) == 3:
            if args[0] == 'range':
                using_range = True
                Command.regenerate_flood_from_range(args[1], args[2])

        if len(args) > 0 and not using_range:
            for a in args:
                print 'Process using celery broker : %s' % a
                process_flood.delay(a).get()

        elif not using_range:
            floods = Flood.objects.all().order_by('-flood')
            print 'Process using celery broker (%s)' % len(floods)
            for flood in floods:
                process_flood.delay(flood.event_id).get()

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
        total_hours = int(time_diff.total_seconds()/3600)
        success = 0
        failed = 0
        for i in range(0, total_hours):
            hour_diff = datetime.timedelta(hours=i+1)
            target_time = start_time + hour_diff
            event_id = target_time.strftime(format_str)
            print 'Processing flood: %s' % event_id
            result = process_flood.delay(event_id)
            is_success = result.get()
            print 'Task result: %s' % is_success
            if is_success:
                success += 1
            else:
                failed += 1

        print 'Regenerate process done'
        print 'Success: %s. Failed: %s' % (success, failed)
