# coding=utf-8
from django.conf.urls import url
from realtime.views import earthquake
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    # default url
    url(r'',
        earthquake.earthquake_list,
        name='earthquake_list'),

    url(r'^api/v1/earthquake/$',
        earthquake.earthquake_list,
        name='earthquake_list'),
    url(r'^api/v1/earthquake/(?P<shake_id>[-\w]+)/$',
        earthquake.earthquake_detail,
        name='earthquake_detail'),
    url(r'^api/v1/earthquake-report/'
        r'(?P<shake_id>[-\d]+)/$',
        earthquake.earthquake_report_list,
        name='earthquake_report_list'),
    url(r'^api/v1/earthquake-report/'
        r'(?P<shake_id>[-\d]+)/'
        r'(?P<language>[-\w]+)/$',
        earthquake.earthquake_report_detail,
        name='earthquake_report_detail')
]

urlpatterns = format_suffix_patterns(urlpatterns)
