# coding=utf-8
from django.conf.urls import patterns, url
from realtime.views.earthquake import (
    earthquake_feature_list,
    index,
    get_earthquakes,
    populate,
    EarthquakeList,
    EarthquakeDetail,
    EarthquakeReportList,
    EarthquakeReportDetail
    )
from realtime.views import root
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^api/v1/$', root.api_root),
    url(r'^api/v1/earthquake/$',
        EarthquakeList.as_view(),
        name='earthquake_list'),
    url(r'^api/v1/earthquake-feature/$',
        earthquake_feature_list,
        name='earthquake_feature_list'),
    url(r'^api/v1/earthquake/(?P<shake_id>[-\w]+)/$',
        EarthquakeDetail.as_view(),
        name='earthquake_detail'),
    url(r'^api/v1/earthquake-report/$',
        EarthquakeReportList.as_view(),
        name='earthquake_report_list'),
    url(r'^api/v1/earthquake-report/'
        r'(?P<shake_id>[-\d]+)/$',
        EarthquakeReportList.as_view(),
        name='earthquake_report_list'),
    url(r'^api/v1/earthquake-report/'
        r'(?P<shake_id>[-\d]+)/'
        r'(?P<language>[-\w]+)/$',
        EarthquakeReportDetail.as_view(),
        name='earthquake_report_detail')
    ]

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns.extend(
    patterns(
        '',
        url(r'^$',
            index,
            name='index'),
        url(r'^get_earthquakes[/.*]$',
            get_earthquakes,
            name='get_earthquakes'),
        url(r'^populate$',
            populate,
            name='populate'),
    )
)
