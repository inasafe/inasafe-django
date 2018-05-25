# coding=utf-8
import os
import shutil
from tempfile import mkdtemp

from django.core.management.base import BaseCommand
from realtime.tasks.realtime.test.test_realtime_tasks import TestFloodTasks

from realtime.tasks.realtime.flood import process_flood


class Command(BaseCommand):
    """Script to load flood test data for demo purpose only.

    """
    help = 'Script to load flood test data for demo purpose only.'

    def handle(self, *args, **options):
        # Copy file to hazard drop directory
        REALTIME_HAZARD_DROP = os.environ.get(
            'REALTIME_HAZARD_DROP',
            '/home/realtime/hazard-drop/')
        hazard_drop_path = mkdtemp(dir=REALTIME_HAZARD_DROP)
        flood_layer_uri = TestFloodTasks.fixtures_path('flood_data.json')
        hazard_drop_path = os.path.join(
            hazard_drop_path, os.path.basename(flood_layer_uri))
        print 'Copy flood data to %s' % hazard_drop_path
        shutil.copy(flood_layer_uri, hazard_drop_path)

        flood_id = '2018022511-6-rw'
        print 'Send flood data to InaSAFE Django with flood id = %s' % flood_id
        process_flood.delay(
            flood_id=flood_id,
            data_source='hazard_file',
            data_source_args={
                'filename': hazard_drop_path
            }
        )
