# coding=utf-8
from realtime.models.earthquake import EarthquakeReport
from rest_framework.test import APIClient

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '19/06/15'


def report_pdf(request, shake_id, language=u'id', language2=u'id'):
    report = EarthquakeReport.objects.get(
        earthquake__shake_id=shake_id,
        language=language)
    client = APIClient()
    return client.get(report.report_pdf.url)


def report_image(request, shake_id, language=u'id', language2=u'id'):
    report = EarthquakeReport.objects.get(
        earthquake__shake_id=shake_id,
        language=language)
    client = APIClient()
    return client.get(report.report_image.url)


def report_thumbnail(request, shake_id, language=u'id', language2=u'id'):
    report = EarthquakeReport.objects.get(
        earthquake__shake_id=shake_id,
        language=language)
    client = APIClient()
    return client.get(report.report_thumbnail.url)
