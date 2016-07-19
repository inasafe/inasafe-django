# coding=utf-8
"""Forms for realtime app."""
import datetime
from bootstrap3_datetime.widgets import DateTimePicker

from django import forms
from django.utils.translation import ugettext_lazy as _
from realtime.models.earthquake import Earthquake
from realtime.models.ash import Ash


class EarthquakeForm(forms.ModelForm):
    class Meta:
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
datetime_picker = DateTimePicker(
    format=date_format,
    options={
        'pickTime': False
    })


class FilterForm(forms.Form):
    start_date = forms.DateField(widget=DateTimePicker(
        format=date_format,
        options={
            'pickTime': False
        }),
        label=_('Start Date'))
    end_date = forms.DateField(widget=DateTimePicker(
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


class AshUploadForm(forms.ModelForm):

    class Meta:
        model = Ash
        fields = [
            'volcano_name',
            'volcano',
            # 'volcano_name',
            # 'location',
            'alert_level',
            # 'eruption_height',
            'event_time',
            # 'region',
            'hazard_file'
        ]

    event_time = forms.DateTimeField(initial=datetime.datetime.now())
    volcano_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'autocomplete': 'off'}))
