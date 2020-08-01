# coding=utf-8
from __future__ import print_function
from django.core.management.base import BaseCommand

from realtime.models.volcano import load_volcano_data, Volcano

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '7/18/16'


class Command(BaseCommand):
    """Script to check indicator status. Can be executed via cronjob

    """
    help = 'Command to re-execute flood process on existing event id'

    def handle(self, *args, **options):
        if not len(args) == 2:
            print('Please provide filename')
            return

        volcano_shapefile = args[1]
        load_volcano_data(Volcano, volcano_shapefile)
