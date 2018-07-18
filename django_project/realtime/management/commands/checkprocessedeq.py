# coding=utf-8
import datetime
import logging

from django.core.management.base import BaseCommand

from realtime.app_settings import ANALYSIS_LANGUAGES
from realtime.models.earthquake import Earthquake

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'


LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """Script to check earthquake processing status. Can be executed via cronjob.

    """
    help = 'Command to check unprocessed eq.'

    def add_arguments(self, parser):

        parser.add_argument(
            '--since',
            type=str,
            dest='since',
            help='end date - format YYYY/MM/DD'
        )

        parser.add_argument(
            '--dry_run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Just checcking without processing.')

    def handle(self, *args, **options):

        dry_run = options.get('dry_run')

        since = options.get('since')

        try:
            since = datetime.datetime.strptime(since, '%Y/%m/%d')
        except BaseException:
            since = None

        qs = Earthquake.objects.all()

        if since:
            print 'Checking only since: {0}'.format(since)
            qs = qs.filter(time__gte=since)

        # tuple of eq object and language for unprocessed impacts
        unprocessed_impacts = []

        # tuple of eq object and language for unprocessed reports
        unprocessed_reports = []

        for _e in qs:
            eq = _e
            """:type: Earthquake"""

            for lang in ANALYSIS_LANGUAGES:
                eq.inspected_language = lang

                if not eq.impact_layer_exists:
                    unprocessed_impacts.append((eq, lang))
                    continue

                if not eq.has_reports:
                    unprocessed_reports.append((eq, lang))

        if dry_run:
            print 'Dry Run result.'

        print 'Unprocessed impacts:'

        for tup in unprocessed_impacts:
            lang = tup[1]
            eq = tup[0]
            """:type: Earthquake"""

            print '{0} {1}'.format(lang, eq)

            if not dry_run:
                eq.inspected_language = lang
                eq.rerun_analysis()
                eq.rerun_report_generation()

        print 'Total Unprocessed impacts ({0})'.format(
            len(unprocessed_impacts))
        print ''
        print 'Unprocessed reports:'

        for tup in unprocessed_reports:
            lang = tup[1]
            eq = tup[0]
            """:type: Earthquake"""

            print '{0} {1}'.format(lang, eq)
            if not dry_run:
                eq.inspected_language = lang
                eq.rerun_report_generation()

        print 'Total Unprocessed reports ({0})'.format(
            len(unprocessed_reports))
        print ''
        print('Command finished.')
