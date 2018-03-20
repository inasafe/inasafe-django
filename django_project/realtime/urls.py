# coding=utf-8
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from realtime.views import user_push, root
from realtime.views.ash import (
    index as ash_index,
    upload_form as ash_upload_form, AshList, AshReportList, AshReportDetail,
    AshDetail, AshFeatureList, ash_report_map)
from realtime.views.earthquake import (
    index as shake_index,
    EarthquakeList,
    EarthquakeDetail,
    EarthquakeReportList,
    EarthquakeReportDetail,
    EarthquakeFeatureList, iframe_index, get_grid_xml, get_analysis_zip,
    EarthquakeMMIContourList)
from realtime.views.flood import (
    index as flood_index,
    FloodList,
    FloodDetail,
    FloodReportList,
    FloodReportDetail, FloodEventList, flood_event_features,
    impact_event_features, rw_flood_frequency, rw_histogram,
    flood_impact_report, flood_impact_map, get_flood_data_json)
from realtime.views.reports import latest_report
from realtime.views.volcano import VolcanoFeatureList, VolcanoList

urlpatterns = [
    url(r'^api/v1/$', root.api_root, name='api_root'),

    # Earthquake
    url(r'^api/v1/earthquake/(?P<shake_id>[-\w]+)/$',
        EarthquakeList.as_view(),
        name='earthquake_list'),
    url(r'^api/v1/earthquake/$',
        EarthquakeList.as_view(),
        name='earthquake_list'),
    url(r'^api/v1/earthquake-feature/$',
        EarthquakeFeatureList.as_view(),
        name='earthquake_feature_list'),
    url(r'^api/v1/earthquake/(?P<shake_id>[-\w]+)/'
        r'(?P<source_type>\w*)/$',
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
        r'(?P<source_type>\w*)/$',
        EarthquakeReportList.as_view(),
        name='earthquake_report_list'),
    url(r'^api/v1/earthquake-report/'
        r'(?P<shake_id>[-\d]+)/'
        r'(?P<source_type>\w*)/'
        r'(?P<language>[-\w]+)/$',
        EarthquakeReportDetail.as_view(),
        name='earthquake_report_detail'),
    url(r'^api/v1/earthquake-mmi-contours/'
        r'(?P<shake_id>[-\d]+)/'
        r'(?P<source_type>\w*)/$',
        EarthquakeMMIContourList.as_view(),
        name='earthquake_mmi_contours_list'),
    url(r'^api/v1/earthquake-mmi-contours/$',
        EarthquakeMMIContourList.as_view(),
        name='earthquake_mmi_contours_list'),

    # Flood
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
    url(r'^api/v1/flood-impact-event-features/'
        r'(?P<event_id>\d{10}-(1|3|6)-(rw|village|subdistrict))/$',
        impact_event_features,
        name='flood_impact_event_features'),
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

    # Volcano
    url(r'^api/v1/volcano-feature/$',
        VolcanoFeatureList.as_view(),
        name='volcano_feature_list'),
    url(r'^api/v1/volcano-list/$',
        VolcanoList.as_view(),
        name='volcano_list'),

    # Ash
    url(r'^api/v1/ash/$',
        AshList.as_view(),
        name='ash_list'),
    url(r'^api/v1/ash-report/$',
        AshReportList.as_view(),
        name='ash_report_list'),
    url(r'^api/v1/ash/'
        r'(?P<volcano_name>[\w -]+)/'
        r'(?P<event_time>[\d+-]{19})/$',
        AshDetail.as_view(),
        name='ash_detail'),
    url(r'^api/v1/ash-report/'
        r'(?P<volcano_name>[\w -]+)/$',
        AshReportList.as_view(),
        name='ash_report_list'),
    url(r'^api/v1/ash-report/'
        r'(?P<volcano_name>[\w -]+)/'
        r'(?P<event_time>[\d+-]{19})/$',
        AshReportList.as_view(),
        name='ash_report_list'),
    url(r'^api/v1/ash-report/'
        r'(?P<volcano_name>[\w -]+)/'
        r'(?P<event_time>[\d+-]{19})/'
        r'(?P<language>[-\w]+)/$',
        AshReportDetail.as_view(),
        name='ash_report_detail'),
    url(r'^api/v1/ash-feature/$',
        AshFeatureList.as_view(),
        name='ash_feature_list'),
]

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    url(r'^$', shake_index, name='index'),

    # Shake
    url(r'^shake/$', shake_index, name='shake_index'),
    url(r'^shake/grid/(?P<shake_id>[-\d]+)/'
        r'(?P<source_type>\w*)/$',
        get_grid_xml,
        name='shake_grid'),
    url(r'^shake/analysis/(?P<shake_id>[-\d]+)/'
        r'(?P<source_type>\w*)/$',
        get_analysis_zip,
        name='analysis_zip'),

    # Flood
    url(r'^flood/$', flood_index, name='flood_index'),
    url(r'^flood/impact-report/'
        r'(?P<event_id>\d{10}-(1|3|6)-(rw|village|subdistrict))/'
        r'(?P<language>[-\w]+)/$',
        flood_impact_report,
        name='flood_impact_report'),
    url(r'^flood/impact-map/'
        r'(?P<event_id>\d{10}-(1|3|6)-(rw|village|subdistrict))/'
        r'(?P<language>[-\w]+)/$',
        flood_impact_map,
        name='flood_impact_map'),
    url(r'^flood/flood-data/'
        r'(?P<event_id>\d{10}-(1|3|6)-(rw|village|subdistrict))/$',
        get_flood_data_json,
        name='flood_data'),

    # Ash
    url(r'^ash/$', ash_index, name='ash_index'),
    url(r'^ash/upload$', ash_upload_form, name='ash_upload_form'),
    url(r'^ash/report-map/'
        r'(?P<volcano_name>[\w -]+)/'
        r'(?P<event_time>[\d+-]{19})/'
        r'(?P<language>[-\w]+)/$',
        ash_report_map,
        name='ash_report_map'),

    # IFrame
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
        name='latest_report'),
    url(r'^rw-flood-frequency/(?P<hazard_levels_string>[\d,]*)',
        rw_flood_frequency,
        name='rw_flood_frequency'),
    url(r'^rw-histogram/'
        r'(?P<boundary_id>\w+)/'
        r'(?P<hazard_levels_string>[\d,]*)/'
        r'(?P<start_date_timestamp>[\w-]*)/'
        r'(?P<end_date_timestamp>[\w-]*)',
        rw_histogram,
        name='rw_histogram'),
]
