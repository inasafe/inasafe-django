# coding=utf-8
from django.core.management.base import BaseCommand
from realtime.scripts.check_indicators import check_indicator_status

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/09/15'


class Command(BaseCommand):
    """Script to check indicator status. Can be executed via cronjob

    """
    help = 'Script to check indicator status. Can be executed via cronjob.'

    def handle(self, *args, **options):
        check_indicator_status()
