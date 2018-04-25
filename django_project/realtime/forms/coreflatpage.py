# coding=utf-8

from django import forms
from django.utils import translation
from realtime.models.coreflatpage import CoreFlatPage
from tinymce.widgets import TinyMCE

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'


class CoreFlatPageForm(forms.ModelForm):
    """Override form to allow tinyMCE for content field"""

    content = forms.CharField(
        widget=TinyMCE(
            attrs={
                'cols': 80,
                'rows': 30,

            },
            content_language=translation.get_language()
        )
    )

    class Meta:
        model = CoreFlatPage
        fields = '__all__'
