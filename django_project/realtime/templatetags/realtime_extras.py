# coding=utf-8
from django import template
from django.utils.translation import ugettext as _


__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '02/09/15'

register = template.Library()


@register.filter
def naturaltimedelta(value):
    """
    Finds the difference between the datetime value given and now()
    and returns appropriate humanize form
    """

    from datetime import timedelta

    if isinstance(value, timedelta):
        delta = value
        text = []
        if delta.days > 1:
            # example: 10 days
            text.append(_('%d days') % delta.days)
        if delta.seconds > 3600:
            # example: 10 hours
            text.append(_('%d hours') % (delta.seconds / 3600, ))
        if delta.seconds % 3600 > 60:
            # example: 10 minutes
            text.append(_('%d minutes') % ((delta.seconds % 3600) / 60, ))
        if (delta.seconds % 3600) / 60 > 0:
            # example: 10 seconds
            text.append(_('%d seconds') % (((delta.seconds % 3600) % 60),))
        if len(text) == 0:
            return _('%d microseconds') % delta.microseconds
        return ', '.join(text)
    else:
        return str(value)
