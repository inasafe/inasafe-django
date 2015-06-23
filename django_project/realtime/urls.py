# coding=utf-8
from django.conf.urls import url
from realtime.views.earthquake import (
    earthquake_list,
    earthquake_feature_list,
    earthquake_detail,
    index,
    get_earthquakes,
    populate
    )
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import patterns, url

urlpatterns = [
    url(r'^api/v1/earthquake/$',
        earthquake_list,
        name='earthquake_list'),
    url(r'^api/v1/earthquake-feature/$',
        earthquake_feature_list,
        name='earthquake_feature_list'),
    url(r'^api/v1/earthquake/(?P<shake_id>[-\w]+)/$',
        earthquake_detail,
        name='earthquake_detail')
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
