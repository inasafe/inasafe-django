# coding=utf-8

from __future__ import print_function
from django.core.management.base import BaseCommand
from django.db.models import Count

from realtime.models import Boundary

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/09/15'


class Command(BaseCommand):
    """Command to validate boundary tables

    """
    help = 'Command to validate boundary tables'

    def handle(self, *args, **options):
        # Find duplicate boundary and delete it
        aggregate_boundaries = Boundary.objects.values(
            'upstream_id',
            'name',
            'parent').annotate(boundary_count=Count('name'))
        duplicate_boundaries = aggregate_boundaries.filter(
            boundary_count__gt=1)

        print('Total duplicate boundaries: {}'.format(
            duplicate_boundaries.count()))

        for b in duplicate_boundaries:
            boundary = Boundary.objects.filter(upstream_id=b['upstream_id'])
            print('Boundary upstream id: {}'.format(b['upstream_id']))
            boundary.delete()
