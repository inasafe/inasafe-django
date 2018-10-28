# coding=utf-8
import os
from django.db.models.query_utils import Q
from django.conf import settings
from django.core.management.base import BaseCommand
from realtime.models.earthquake import EarthquakeReport

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '10/07/15'


class Command(BaseCommand):
    """Delete orphan report files in media to save spaces.

    """
    help = 'Delete orphan report files in media to save spaces.'

    def handle(self, *args, **options):
        print 'Deleting orphan report files which is not recorded in ' \
              'database.'
        media_root = os.path.relpath(settings.MEDIA_ROOT)
        report_root = 'reports'
        files_root = os.path.abspath(os.path.join(media_root, report_root))
        print 'Folder to process : %s' % files_root
        print 'Media root : %s' % media_root
        print 'Reports root : %s' % report_root
        for folders, _, files in os.walk(files_root):
            for f in files:
                abs_filename = os.path.join(folders, f)
                rel_filename = os.path.relpath(abs_filename, media_root)
                print 'check filena' \
                      'me : %s' % rel_filename
                exists_pdf = EarthquakeReport.objects.filter(
                    Q(report_pdf=rel_filename)
                    | Q(report_thumbnail=rel_filename)
                    | Q(report_image=rel_filename))
                if exists_pdf.count() == 0:
                    try:
                        os.remove(abs_filename)
                        print 'Deleted : %s' % rel_filename
                    except Exception as exc:
                        print exc.message
