# coding=utf-8

from __future__ import print_function
from builtins import input
from django.core.management.base import BaseCommand
from realtime.models.earthquake import Earthquake, EarthquakeReport

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '23/06/15'


class Command(BaseCommand):
    """Generate initial test data for realtime api.

    """
    help = 'Generate initial test data for InaSAFE Realtime API.'

    @staticmethod
    def data_path(filename):
        return u'realtime/tests/data/' + filename

    def handle(self, *args, **options):
        delete_all = input('Delete all existing data? (y/N)')

        if delete_all.lower() == 'y':
            for report in EarthquakeReport.objects.all():
                report.delete()
            EarthquakeReport.objects.all().delete()
            Earthquake.objects.all().delete()
            print('Test data successfully cleared.')
        else:
            print('Cancel execution.')
