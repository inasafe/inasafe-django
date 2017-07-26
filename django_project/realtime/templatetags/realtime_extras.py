# coding=utf-8
from django import template
from django.utils.translation import ugettext as _
from realtime.helpers.base_indicator import Indicator

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '02/09/15'

register = template.Library()


@register.filter
def naturaltimedelta(value, clarity=None):
    """
    Finds the difference between the datetime value given and now()
    and returns appropriate humanize form

    :param value: the value to be filtered
    :type value: Indicator

    :param clarity: the clarity of string detail
    if it is set to 2 then it will only display the first 2 most
    significant time component
    :type clarity: int

    :rtype: str
    """

    from datetime import timedelta

    if isinstance(value, timedelta):
        delta = value
        text = []
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60

        detail = 0
        if not clarity:
            clarity = 5

        if days > 0:
            # example: 10 days
            text.append(_('%d days') % days)
            detail += 1
        if hours > 0 and detail < clarity:
            # example: 10 hours
            text.append(_('%d hours') % hours)
            detail += 1
        if minutes > 0 and detail < clarity:
            # example: 10 minutes
            text.append(_('%d minutes') % minutes)
            detail += 1
        if seconds > 0 and detail < clarity:
            # example: 10 seconds
            text.append(_('%d seconds') % seconds)
        if len(text) == 0:
            return _('%d microseconds') % delta.microseconds
        return ', '.join(text)
    else:
        return str(value)


@register.filter
def indicator_bootstrap_class(value):
    """Get relevant bootstrap label class for an indicator"""

    if isinstance(value, Indicator):
        if value.is_critical():
            return 'danger'
        elif value.is_warning():
            return 'warning'
        elif value.is_healthy():
            return 'success'
        else:
            return None
    else:
        return None
