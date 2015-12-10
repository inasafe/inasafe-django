# coding=utf-8
from django.conf.urls import url
from realtime.views import user_push
from realtime.views.earthquake import (
    index as shake_index,
    EarthquakeList,
    EarthquakeDetail,
    EarthquakeReportList,
    EarthquakeReportDetail,
    EarthquakeFeatureList, iframe_index)
from realtime.views import root
from rest_framework.urlpatterns import format_suffix_patterns

from realtime.views.flood import (
    index as flood_index,
    FloodList,
    FloodDetail,
    FloodReportList,
    FloodReportDetail, FloodEventList, flood_event_features)
from realtime.views.reports import latest_report

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
        name='earthquake_report_detail'),
    url(r'^api/v1/flood/$',
        FloodList.as_view(),
        name='flood_list'),
    url(r'^api/v1/flood-events/$',
        FloodEventList.as_view(),
        name='flood_event_list'),
    url(r'^api/v1/flood-event-features/'
        r'(?P<event_id>\d{10}-(1|3|6)-(rw|village|subdistrict))/$',
        flood_event_features,
        name='flood_event_features'),
    url(r'^api/v1/flood/'
        r'(?P<event_id>\d{10}-(1|3|6)-(rw|village|subdistrict))/$',
        FloodDetail.as_view(),
        name='flood_detail'),
    url(r'^api/v1/flood-report/$',
        FloodReportList.as_view(),
        name='flood_report_list'),
    url(r'^api/v1/flood-report/'
        r'(?P<event_id>\d{10}-(1|3|6)-(rw|village|subdistrict))/$',
        FloodReportList.as_view(),
        name='flood_report_list'),
    url(r'^api/v1/flood-report/'
        r'(?P<event_id>\d{10}-(1|3|6)-(rw|village|subdistrict))/'
        r'(?P<language>[-\w]+)/$',
        FloodReportDetail.as_view(),
        name='flood_report_detail'),

    ]

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    url(r'^$', shake_index, name='index'),
    url(r'^shake/$', shake_index, name='shake_index'),
    url(r'^flood/$', flood_index, name='flood_index'),
    url(r'^iframe$', iframe_index, name='iframe'),
    url(r'^api/v1/is_logged_in/$', root.is_logged_in),
    url(r'^api/v1/indicator/notify_shakemap_push/$',
        user_push.notify_shakemap_push),
    url(r'^indicator$', user_push.indicator, name='indicator'),
    url(r'^indicator/rest_users$',
        user_push.realtime_rest_users,
        name='rest_users'),
    url(r'^latest_report/'
        r'(?P<report_type>(pdf|png|thumbnail))/'
        r'(?P<language>\w*)/?$',
        latest_report,
        name='latest_report')
]
