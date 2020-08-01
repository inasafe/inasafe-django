# coding=utf-8
"""Forms for realtime app."""
from builtins import object
from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from django.utils.translation import ugettext_lazy as _

from realtime.models.earthquake import Earthquake


class EarthquakeForm(forms.ModelForm):
    class Meta(object):
        model = Earthquake
        fields = [
            'shake_id',
            'magnitude',
            'time',
            'depth',
            'location',
            'location_description'
        ]


date_format = 'YYYY-MM-DD'
datetime_format = 'YYYY-MM-DD HH:mm:ss'


class FilterForm(forms.Form):
    start_date = forms.DateField(
        widget=DateTimePicker(
            format=date_format,
            options={
                'pickTime': False
            }),
        label=_('Start Date'))
    end_date = forms.DateField(
        widget=DateTimePicker(
            format=date_format,
            options={
                'pickTime': False
            }),
        label=_('End Date'))
    minimum_magnitude = forms.IntegerField(
        min_value=0,
        max_value=10,
        label=_('Minimum Magnitude'))
    maximum_magnitude = forms.IntegerField(
        min_value=0,
        max_value=10,
        label=_('Maximum Magnitude'))
    # hidden field for felt shakes
    felt = forms.BooleanField()
