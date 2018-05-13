# coding=utf-8
import logging
import os
import re
import shutil

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from realtime.models.earthquake import Earthquake
from realtime.models.flood import Flood
from realtime.models.inasafe_migrations import EarthquakeMigration, \
    FloodMigration

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'


LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """Migration from Realtime 3.5 to InaSAFE v4
    """
    help = 'Command to migrate Realtime'

    def add_arguments(self, parser):
        parser.add_argument(
            '--shakemaps',
            dest='shakemaps')

        parser.add_argument(
            '--shakemaps-extracted',
            dest='shakemaps-extracted')

        parser.add_argument(
            '--shakemaps-corrected',
            dest='shakemaps-corrected'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False
        )

    def handle(self, *args, **options):

        shakemap_raw_dir = options.pop('shakemaps')
        shakemap_extracted_dir = options.pop('shakemaps-extracted')
        shakemap_corrected = options.pop('shakemaps-corrected')
        dry_run = options.pop('dry_run')

        scan_eq_events(dry_run)
        scan_eq_raw_files(shakemap_raw_dir, dry_run)
        scan_eq_raw_files(shakemap_extracted_dir, dry_run)
        scan_eq_raw_files(shakemap_corrected, dry_run)

        clean_up_eq(dry_run)

        scan_flood_events(dry_run)

        clean_up_flood(dry_run)


def scan_eq_events(dry_run=False):
    """Scan EQ events in database and mark for migrations"""
    EarthquakeMigration.scan_migration_state()

    unmigrated = EarthquakeMigration.objects.filter(
        has_shake_grid_in_database=False)
    if not unmigrated:
        print 'All EQ events migrated.'

    if dry_run:
        for state in unmigrated.iterator():
            print state
        return

    for state in unmigrated.iterator():

        state.migrate_shake_grid()
        # MMI migrated were handled in bulk differently

        state.mark_migrated()

        print 'EQ Migrated {0} {1}'.format(state.event.shake_id, state.migrated)


def clean_up_eq(dry_run=False):
    """Clean up files in media if saved."""
    undeleted = EarthquakeMigration.objects.filter(
        has_shake_grid_in_database=True,
        has_shake_grid_in_media_file=True)

    if not undeleted:
        print 'All EQ events cleaned up.'

    if dry_run:
        for state in undeleted.iterator():
            print state
        return

    for state in undeleted.iterator():

        state.migrate_shake_grid()
        state.mark_migrated()
        print state

    # search stale files
    media_root = settings.MEDIA_ROOT
    grid_media_path = os.path.join(media_root, 'earthquake/grid')

    print 'Find stale shake grid file in media.'
    print

    for path in os.listdir(grid_media_path):
        abs_path = os.path.join(grid_media_path, path)
        if os.path.isfile(abs_path):
            found = True
            try:
                Earthquake.objects.get(shake_grid__endswith=path)
            except Earthquake.DoesNotExist:
                found = False

            print '[{0}] found: [{1}]'.format(path, found)

            if not found:
                os.remove(abs_path)
                print 'Deleted [{0}]'.format(path)


def scan_eq_raw_files(raw_dir, dry_run=False):
    """Scan EQ Raw files in database and mark for migrations"""

    try:

        shake_id_pattern = r'(?P<shake_id>[-_\d]+)'
        pattern = re.compile(shake_id_pattern)

        for path in os.listdir(raw_dir):
            abs_path = os.path.join(raw_dir, path)
            if not os.path.isdir(abs_path):
                continue

            match = pattern.search(path)

            if not match:
                continue

            shake_id = match.group('shake_id')

            try:
                event = Earthquake.objects.get(shake_id=shake_id)
                state = event.migration_state.first()
                """:type: EarthquakeMigration"""

                if state.has_shake_grid_in_database or \
                        state.has_shake_grid_in_media_file:
                    # Do not process if we have it in database.
                    continue

            except Earthquake.DoesNotExist:
                event = Earthquake(shake_id=shake_id)
                event.analysis_flag = False
                event.save()
                state = EarthquakeMigration.objects.create(
                    event=event,
                    has_shake_grid_in_raw_file=True)

            if dry_run:
                print state
                continue

            # get relative grid file
            # legacy location
            grid_file = os.path.join(
                abs_path,
                'output/grid.xml')

            if not os.path.exists(grid_file):
                # new location
                grid_file = os.path.join(
                    abs_path,
                    'grid.xml')

            if not os.path.exists(grid_file):
                state.check_shake_grid_status()
                state.check_mmi_status()
                continue

            # move filename to media
            filename = 'grid-{0}.xml'.format(shake_id)
            g = open(grid_file)
            event.shake_grid.save(filename, File(g), save=True)
            state.check_shake_grid_status()
            state.check_mmi_status()

            state.migrate_shake_grid()
            state.mark_migrated()

    except BaseException as e:
        print e


def scan_flood_events(dry_run=False):
    """Scan EQ events in database and mark for migrations"""
    FloodMigration.scan_migration_state()

    unmigrated = FloodMigration.objects.filter(migrated=False)
    if not unmigrated:
        print 'All Flood events migrated.'

    if dry_run:
        for state in unmigrated.iterator():
            print state
        return

    for state in unmigrated.iterator():

        state.migrate_hazard()
        state.migrate_impact()

        state.mark_migrated()

        print 'Flood Migrated {0} {1}'.format(
            state.event.event_id_formatted,
            state.migrated)


def clean_up_flood(dry_run=False):
    """Clean up files in media if saved."""
    undeleted = FloodMigration.objects.filter(
        has_hazard_in_database=True,
        has_hazard_in_media_file=True)
    undeleted = undeleted | FloodMigration.objects.filter(
        has_impact_in_database=True,
        has_impact_in_media_file=True)
    if not undeleted:
        print 'All Flood events cleaned up.'

    if dry_run:
        for state in undeleted.iterator():
            print state
        return

    for state in undeleted.iterator():

        state.migrate_hazard()
        state.migrate_impact()

        state.mark_migrated()

        print state

    # search stale files
    media_root = settings.MEDIA_ROOT
    media_path = os.path.join(media_root, 'reports/flood/zip')

    print 'Find stale flood data file in media.'
    print

    for path in os.listdir(media_path):
        abs_path = os.path.join(media_path, path)
        if os.path.isfile(abs_path):
            found = True
            try:
                Flood.objects.get(hazard_layer__endswith=path)
            except Flood.DoesNotExist:
                found = False

            print '[{0}] found: [{1}]'.format(path, found)

            if not found:
                os.remove(abs_path)
                print 'Deleted [{0}]'.format(path)
