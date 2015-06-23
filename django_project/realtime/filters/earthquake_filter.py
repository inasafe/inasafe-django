# coding=utf-8
import django_filters
from realtime.models.earthquake import Earthquake

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '23/06/15'


class EarthquakeFilter(django_filters.FilterSet):

    magnitude_max = django_filters.NumberFilter(name='magnitude',
                                                lookup_type='lte')
    magnitude_min = django_filters.NumberFilter(name='magnitude',
                                                lookup_type='gte')
    time_max = django_filters.DateTimeFilter(name='time', lookup_type='lte')
    time_min = django_filters.DateTimeFilter(name='time', lookup_type='gte')
    depth_max = django_filters.NumberFilter(name='depth', lookup_type='lte')
    depth_min = django_filters.NumberFilter(name='depth', lookup_type='gte')
    location_description = django_filters.CharFilter(
        name='location_description', lookup_type='iexact')

    class Meta:
        model = Earthquake
        fields = ['shake_id', 'magnitude_max', 'magnitude_min', 'time_max',
                  'time_min', 'depth_max', 'depth_min',
                  'location_description']
