# coding=utf-8
import os
import shutil
import tempfile
from zipfile import ZipFile

from django.conf import settings
from django.core.management import BaseCommand

from realtime.models.flood import Flood


class Command(BaseCommand):

    @staticmethod
    def extract_flood_data(flood, root_dir):
        """

        :param flood:
        :type flood: Flood
        :return:
        """

        if flood.hazard_layer:

            extract_dir = tempfile.mkdtemp()

            with ZipFile(flood.hazard_layer, 'r') as zf:

                zf.extractall(extract_dir, zf.namelist())

            # search flood data
            layer_filename = os.path.join(extract_dir, 'flood_data.json')

            if not os.path.exists(layer_filename):
                layer_filename = os.path.join(extract_dir,
                                              'flood_data.geojson')

            target_filename = '{0}.json'.format(flood.event_id)

            shutil.copy(layer_filename,
                        os.path.join(root_dir, target_filename))

            shutil.rmtree(extract_dir)

    def handle(self, *args, **options):

        media_root = settings.MEDIA_ROOT
        target_dir = os.path.join(media_root, 'flood_data')

        for flood in Flood.objects.all().iterator():
            print '[{0}]'.format(flood.event_id)
            self.extract_flood_data(flood, target_dir)

        print 'Finished.'
