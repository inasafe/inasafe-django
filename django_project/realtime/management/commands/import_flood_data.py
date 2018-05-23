# coding=utf-8
import os

from django.conf import settings
from django.core.management import BaseCommand

from realtime.models.flood import Flood


class Command(BaseCommand):
    def handle(self, *args, **options):

        media_root = settings.MEDIA_ROOT
        target_dir = os.path.join(media_root, 'flood_data')

        for flood in Flood.objects.all().iterator():
            flood_data_filename = os.path.join(
                target_dir,
                '{0}.json'.format(flood.event_id))
            if os.path.exists(flood_data_filename):

                print 'Processing: [{0}]'.format(flood_data_filename)

                with open(flood_data_filename) as f:
                    flood.flood_data = f.read()
                    flood.save()

        print 'Finished.'
