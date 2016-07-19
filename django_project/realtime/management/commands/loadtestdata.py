# coding=utf-8
import datetime
import shutil
from django.conf import settings
import pytz

from django.contrib.gis.geos.point import Point
from django.core.files.base import File
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
        delete_all = raw_input('Delete all existing data? (y/N)')

        if delete_all.lower() == 'y':
            for report in EarthquakeReport.objects.all():
                report.delete()
            EarthquakeReport.objects.all().delete()
            Earthquake.objects.all().delete()

            shutil.rmtree(settings.MEDIA_ROOT + "/reports")

            Earthquake.objects.create(
                shake_id='20150619200628',
                magnitude=4.6,
                time=datetime.datetime(
                    2015, 6, 19, 20, 6, 28,
                    tzinfo=pytz.timezone('Asia/Jakarta')),
                depth=10,
                location=Point(x=126.52, y=4.16, srid=4326),
                location_description='Manado'
            )
            earthquake = Earthquake.objects.get(shake_id='20150619200628')
            earthquake.save()
            languages = ['id', 'en']
            for l in languages:
                report_pdf = '%s-%s.pdf' % (earthquake.shake_id, l)
                report_png = '%s-%s.png' % (earthquake.shake_id, l)
                report_thumb = '%s-thumb-%s.png' % (earthquake.shake_id, l)
                report = EarthquakeReport()
                report.language = l
                report.earthquake = earthquake
                with open(self.data_path(report_pdf)) as pdf:
                    report.report_pdf = File(pdf)
                    report.save()
                with open(self.data_path(report_png)) as png:
                    report.report_image = File(png)
                    report.save()
                with open(self.data_path(report_thumb)) as thumb:
                    report.report_thumbnail = File(thumb)
                    report.save()
            print 'Test data successfully loaded.'
        else:
            print 'Cancel execution.'
