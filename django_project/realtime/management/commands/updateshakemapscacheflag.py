# coding=utf-8
import logging

from django.core.management.base import BaseCommand

from realtime.models.earthquake import Earthquake

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'


LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """Script to check has_corrected status of a shakemaps

    """
    help = 'Command to check cache flags of shakemaps'

    def handle(self, *args, **options):

        earthquakes = Earthquake.objects.all()
        for _eq in earthquakes.iterator():
            eq = _eq
            """:type: Earthquake"""

            if eq.shake_grid_xml:
                Earthquake.objects.filter(id=eq.id).update(
                    shake_grid_saved=True)
                eq.refresh_from_db()

            if eq.source_type == Earthquake.INITIAL_SOURCE_TYPE:
                eq.mark_shakemaps_has_corrected()
                eq.refresh_from_db()
                print 'Inspecting EQ: {0}. Has corrected: {1}'.format(
                    eq.shake_id, eq.has_corrected)

            eq.mark_shakemaps_has_contours()
            eq.refresh_from_db()
            print 'Inspecting EQ: {0}. Has contours: {1}'.format(
                eq.shake_id,
                eq.has_corrected)

        print 'Command finished.'
