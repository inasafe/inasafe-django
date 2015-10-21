# coding=utf-8
import os
from django.conf import settings
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
    except IOError:
        raise Http404()
    except EarthquakeReport.DoesNotExist:
        # if it doesn't exists in the database. Try to get it directly from
        # media folder
        filename = '%s-%s.pdf' % (shake_id, language)
        filename = os.path.join(
            settings.MEDIA_ROOT, 'reports/pdf/%s' % filename)
        try:
            with open(filename) as f:
                return HttpResponse(f, content_type='application/pdf')
        except IOError:
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
    except IOError:
        raise Http404()
    except EarthquakeReport.DoesNotExist:
        # if it doesn't exists in the database. Try to get it directly from
        # media folder
        filename = '%s-%s.png' % (shake_id, language)
        filename = os.path.join(
            settings.MEDIA_ROOT, 'reports/png/%s' % filename)
        try:
            with open(filename) as f:
                return HttpResponse(f, content_type='image/png')
        except IOError:
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
    except IOError:
        raise Http404()
    except EarthquakeReport.DoesNotExist:
        # if it doesn't exists in the database. Try to get it directly from
        # media folder
        filename = '%s-thumb-%s.png' % (shake_id, language)
        filename = os.path.join(
            settings.MEDIA_ROOT, 'reports/png/%s' % filename)
        try:
            with open(filename) as f:
                return HttpResponse(f, content_type='image/png')
        except IOError:
            raise Http404()
