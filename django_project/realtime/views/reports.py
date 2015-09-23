# coding=utf-8
from django.http.response import HttpResponse, Http404
from realtime.models.earthquake import EarthquakeReport

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '19/06/15'


def report_pdf(request, shake_id, language=u'id', language2=u'id'):
    try:
        report = EarthquakeReport.objects.get(
            earthquake__shake_id=shake_id,
            language=language)
        if not language == language2:
            raise Http404()
        return HttpResponse(
            report.report_pdf.read(), content_type='application/pdf')
    except EarthquakeReport.DoesNotExist:
        raise Http404()


def report_image(request, shake_id, language=u'id', language2=u'id'):
    try:
        report = EarthquakeReport.objects.get(
            earthquake__shake_id=shake_id,
            language=language)
        if not language == language2:
            raise Http404()
        return HttpResponse(
            report.report_image.read(), content_type='image/png')
    except EarthquakeReport.DoesNotExist:
        raise Http404()


def report_thumbnail(request, shake_id, language=u'id', language2=u'id'):
    try:
        report = EarthquakeReport.objects.get(
            earthquake__shake_id=shake_id,
            language=language)
        if not language == language2:
            raise Http404()
        return HttpResponse(
            report.report_thumbnail.read(), content_type='image/png')
    except EarthquakeReport.DoesNotExist:
        raise Http404()
