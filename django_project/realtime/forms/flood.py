# coding=utf-8
"""Forms for realtime app."""
from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from django.utils.translation import ugettext_lazy as _

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
    min_people_affected = forms.IntegerField(
        min_value=0,
        label=_('Minimum'))
    max_people_affected = forms.IntegerField(
        min_value=0,
        label=_('Maximum'))
    min_boundary_flooded = forms.IntegerField(
        min_value=0,
        label=_('Minimum'))
    max_boundary_flooded = forms.IntegerField(
        min_value=0,
        label=_('Maximum'))
