# coding=utf-8

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
        if len(args) > 0:
            for a in args:
                print 'Process using celery broker : %s' % a
                process_flood.delay(a)

        else:
            floods = Flood.objects.all().order_by('-flood')
            print 'Process using celery broker (%s)' % len(floods)
            for flood in floods:
                process_flood.delay(flood.event_id)
