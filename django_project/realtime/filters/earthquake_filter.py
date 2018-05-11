# coding=utf-8
import datetime

import django_filters
import pytz
import six
from django_filters.fields import Lookup

from realtime.models.earthquake import Earthquake

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '23/06/15'


class DateTimeDurationFilter(django_filters.NumberFilter):
    """Used to filter DateTime field based on duration."""

    def filter(self, qs, value):
        if isinstance(value, Lookup):
            lookup = six.text_type(value.lookup_type)
            value = value.value
        else:
            lookup = self.lookup_type
        if value in ([], (), {}, None, ''):
            return qs

        # Handle duration values
        parsed_name = lookup.split('__')
        today = pytz.utc.fromutc(datetime.datetime.utcnow())
        if len(parsed_name) == 2:
            duration_field = parsed_name[1]
            duration_lookup = parsed_name[0]
            if duration_field == 'days':
                duration_value = today - datetime.timedelta(days=int(value))
            elif duration_field == 'hours':
                duration_value = today - datetime.timedelta(hours=int(value))
            else:
                duration_value = today

            qs = self.get_method(qs)(
                **{'%s__%s' % (self.name, duration_lookup): duration_value})

        else:
            qs = self.get_method(qs)(
                **{'%s__%s' % (self.name, lookup): value})

        if self.distinct:
            qs = qs.distinct()
        return qs


class EarthquakeFilter(django_filters.FilterSet):

    max_magnitude = django_filters.NumberFilter(name='magnitude',
                                                lookup_type='lte')
    min_magnitude = django_filters.NumberFilter(name='magnitude',
                                                lookup_type='gte')
    max_time = django_filters.DateTimeFilter(name='time', lookup_type='lte')
    min_time = django_filters.DateTimeFilter(name='time', lookup_type='gte')

    # filter by recent days or hours
    since_last_days = DateTimeDurationFilter(
        name='time', lookup_type='gte__days')
    since_last_hours = DateTimeDurationFilter(
        name='time', lookup_type='gte__hours')

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
                  'since_last_days', 'since_last_hours',
                  'location_description']
