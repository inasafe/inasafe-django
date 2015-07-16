# coding=utf-8
from django.conf.urls import url
from realtime.views.earthquake import (
    index,
    EarthquakeList,
    EarthquakeDetail,
    EarthquakeReportList,
    EarthquakeReportDetail,
    EarthquakeFeatureList, iframe_index)
from realtime.views import root
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^api/v1/$', root.api_root, name='api_root'),
    url(r'^api/v1/earthquake/$',
        EarthquakeList.as_view(),
        name='earthquake_list'),
    url(r'^api/v1/earthquake-feature/$',
        EarthquakeFeatureList.as_view(),
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

urlpatterns += [
    url(r'^$', index, name='index'),
    url(r'^iframe$', iframe_index, name='iframe'),
]
