# coding=utf-8
from django.conf.urls import url
from realtime.views import reports

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '23/06/15'


# urlpatterns for Realtime Reports
urlpatterns = [
    url(r'^(?P<language>[-\w]+)/'
        r'(?P<shake_id>[-\d]+)-(?P<language2>[-\w]+).pdf$',
        reports.report_pdf,
        name='report_pdf'),
    url(r'^(?P<language>[-\w]+)/'
        r'(?P<shake_id>[-\d]+)-thumb-(?P<language2>[-\w]+).png$',
        reports.report_thumbnail,
        name='report_thumbnail'),
    url(r'^(?P<language>[-\w]+)/'
        r'(?P<shake_id>[-\d]+)-(?P<language2>[-\w]+).png$',
        reports.report_image,
        name='report_image'),

    # with source type
    url(r'^(?P<language>[-\w]+)/'
        r'(?P<source_type>[\w]+)/'
        r'(?P<shake_id>[-\d]+)-(?P<language2>[-\w]+).pdf$',
        reports.report_pdf,
        name='report_pdf'),
    url(r'^(?P<language>[-\w]+)/'
        r'(?P<source_type>[\w]+)/'
        r'(?P<shake_id>[-\d]+)-thumb-(?P<language2>[-\w]+).png$',
        reports.report_thumbnail,
        name='report_thumbnail'),
    url(r'^(?P<language>[-\w]+)/'
        r'(?P<source_type>[\w]+)/'
        r'(?P<shake_id>[-\d]+)-(?P<language2>[-\w]+).png$',
        reports.report_image,
        name='report_image'),
]
