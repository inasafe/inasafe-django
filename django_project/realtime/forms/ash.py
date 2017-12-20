# coding=utf-8
"""Forms for realtime app."""
from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from django.utils.translation import ugettext_lazy as _
from realtime.models.ash import Ash


datetime_format = 'YYYY-MM-DD HH:mm:ss'


class AshUploadForm(forms.ModelForm):

    class Meta:
        model = Ash
        fields = [
            'volcano_name',
            'volcano',
            # 'volcano_name',
            # 'location',
            'alert_level',
            'eruption_height',
            'event_time',
            'event_time_zone_offset',
            'event_time_zone_string',
            # 'region',
            'hazard_file'
        ]

    event_time = forms.DateTimeField(
        # initial=datetime.datetime.now(),
        widget=DateTimePicker(
            format=datetime_format,
            options={
                'pickTime': True,
                'pickSeconds': True,
            }))
    alert_level = forms.ChoiceField(
        choices=[
            ('normal', 'Normal'),
            ('waspada', 'Waspada'),
            ('siaga', 'Siaga'),
            ('awas', 'Awas')
        ])
    event_time_zone_offset = forms.IntegerField(
        widget=forms.HiddenInput())
    event_time_zone_string = forms.CharField(
        label=_('Timezone'),
        widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    volcano_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'autocomplete': 'off'}))
