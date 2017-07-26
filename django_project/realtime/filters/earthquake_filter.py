# coding=utf-8
import django_filters
from realtime.models.earthquake import Earthquake

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '23/06/15'


class EarthquakeFilter(django_filters.FilterSet):

    max_magnitude = django_filters.NumberFilter(name='magnitude',
                                                lookup_type='lte')
    min_magnitude = django_filters.NumberFilter(name='magnitude',
                                                lookup_type='gte')
    max_time = django_filters.DateTimeFilter(name='time', lookup_type='lte')
    min_time = django_filters.DateTimeFilter(name='time', lookup_type='gte')
    max_depth = django_filters.NumberFilter(name='depth', lookup_type='lte')
    min_depth = django_filters.NumberFilter(name='depth', lookup_type='gte')

    # add redundant filters
    maximum_magnitude = max_magnitude
    minimum_magnitude = min_magnitude
    start_date = min_time
    end_date = max_time

    location_description = django_filters.CharFilter(
        name='location_description', lookup_type='iexact')

    class Meta:
        model = Earthquake
        fields = ['shake_id', 'max_magnitude', 'min_magnitude', 'max_time',
                  'min_time', 'max_depth', 'min_depth',
                  'maximum_magnitude', 'minimum_magnitude',
                  'start_date', 'end_date',
                  'location_description']
