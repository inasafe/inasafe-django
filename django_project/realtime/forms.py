# coding=utf-8
"""Forms for realtime app."""

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


class FilterForm(forms.Form):
    minimum_magnitude = forms.IntegerField()
    maximum_magnitude = forms.IntegerField()
    start_date = forms.DateField()
    end_date = forms.DateField()