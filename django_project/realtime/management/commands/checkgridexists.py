# coding=utf-8
from optparse import make_option

from django.core.management.base import BaseCommand

from realtime.models.earthquake import Earthquake
from realtime.tasks.realtime.earthquake import process_shake

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/09/15'


class Command(BaseCommand):
    """Script to check indicator status. Can be executed via cronjob

    """
    help = 'Script to check grid.xml existance in realtime processor.'
    option_list = BaseCommand.option_list + (
        make_option(
            '--force',
            action='store_true',
            default=False,
            dest='force',
            help='Force pushing the shake_grid'),
    )

    def handle(self, *args, **options):
        shakes = Earthquake.objects.all()
        # filter non existing grid.xml
        if not options['force']:
            print 'Only get non existing grid.xml'
            shakes = [s for s in shakes if not s.shake_grid]
        elif len(args) > 0:
            shakes = Earthquake.objects.filter(shake_id__in=args)
            print 'Only get: %s' % args
        else:
            print 'Get all grid.xml'
        print 'Trying to get grid.xml of shakes (%d)' % len(shakes)
        for shake in shakes:
            # will be executed asyncly using celery
            # print 'Shake id: %s' % shake.shake_id
            process_shake.delay(shake.shake_id)
