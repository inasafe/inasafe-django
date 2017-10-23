# coding=utf-8

from django.core.management.base import BaseCommand
from realtime.models.earthquake import Earthquake

from realtime.tasks.realtime.earthquake import shake_folder_list, \
    process_shake

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/09/15'


class Command(BaseCommand):
    """Script to check missing shakes

    """
    help = 'Script to check missing shakes from processors.'

    def handle(self, *args, **options):
        # Get all shakes folder list
        dir_list = shake_folder_list.delay().get()

        # Get all shakes id list
        shake_id_list = Earthquake.objects.all().values('shake_id')
        shake_id_list = [s['shake_id'] for s in shake_id_list]

        # Take shakes that is not currently on models
        missing_shakes = list(set(dir_list) - set(shake_id_list))

        print 'Missing shakes:'
        for s in missing_shakes:
            print s

        process = raw_input('Process these shakes? (y/N)')

        if process.lower() == 'y':
            for s in missing_shakes:
                print 'Process shake %s' % (s, )
                process_shake.delay(s)
