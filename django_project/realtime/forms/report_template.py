# coding=utf-8
"""Forms for realtime app."""
from django import forms
from django.utils.translation import ugettext_lazy as _

from realtime.models.report_template import ReportTemplate

__author__ = 'myarjunar'
__project_name__ = 'inasafe-django'
__filename__ = 'report_template'
__date__ = '7/15/16'
__copyright__ = 'myarjuanar@gmail.com'

datetime_format = 'YYYY-MM-DD HH:mm:ss'


class ReportTemplateUploadForm(forms.ModelForm):

    class Meta:
        model = ReportTemplate
        fields = [
            'hazard',
            'language',
            'notes',
            'version',
            'template_file'
        ]

    hazard = forms.ChoiceField(
        label=_('Hazard'),
        choices=[
            ('earthquake', _('Earthquake')),
            ('flood', _('Flood')),
            ('ash', _('Volcanic Ash')),
        ])

    language = forms.ChoiceField(
        label=_('Language'),
        choices=[
            ('id', _('Bahasa Indonesia')),
            ('en', _('English'))
        ])

    notes = forms.CharField(
        max_length=50,
        label=_('Notes'),
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )

    version = forms.CharField(
        max_length=10,
        label=_('Version'),
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )
