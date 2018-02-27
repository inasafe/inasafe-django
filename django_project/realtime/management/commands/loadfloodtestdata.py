# coding=utf-8
from django.core.management.base import BaseCommand

from realtime.tasks.test.test_realtime_tasks import flood_layer_uri
from realtime.tasks.realtime.flood import process_flood


class Command(BaseCommand):
    """Script to load flood test data for demo purpose only.

    """
    help = 'Script to load flood test data for demo purpose only.'

    def handle(self, *args, **options):
        flood_id = '2018022511-6-rw'
        print 'Send flood data to InaSAFE Django with flood id = %s' % flood_id
        process_flood.delay(
            flood_id=flood_id,
            data_source='hazard_file',
            data_source_args={
                'filename': flood_layer_uri
            }
        )
