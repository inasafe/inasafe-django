# coding=utf-8
from django.conf.urls import url
from realtime.views import earthquake
from realtime.views import root
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^api/v1/$', root.api_root),
    url(r'^api/v1/earthquake/$',
        earthquake.EarthquakeList.as_view(),
        name='earthquake_list'),
    url(r'^api/v1/earthquake/(?P<shake_id>[-\w]+)/$',
        earthquake.EarthquakeDetail.as_view(),
        name='earthquake_detail'),
    url(r'^api/v1/earthquake-report/$',
        earthquake.EarthquakeReportList.as_view(),
        name='earthquake_report_list'),
    url(r'^api/v1/earthquake-report/'
        r'(?P<shake_id>[-\d]+)/$',
        earthquake.EarthquakeReportList.as_view(),
        name='earthquake_report_list'),
    url(r'^api/v1/earthquake-report/'
        r'(?P<shake_id>[-\d]+)/'
        r'(?P<language>[-\w]+)/$',
        earthquake.EarthquakeReportDetail.as_view(),
        name='earthquake_report_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
