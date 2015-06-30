# coding=utf-8
"""Forms for realtime app."""
from bootstrap3_datetime.widgets import DateTimePicker

from django import forms
from realtime.models.earthquake import Earthquake


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
        }))
    end_date = forms.DateField(widget=DateTimePicker(
        format=date_format,
        options={
            'pickTime': False
        }))
    minimum_magnitude = forms.IntegerField(min_value=0, max_value=10)
    maximum_magnitude = forms.IntegerField(min_value=0, max_value=10)
