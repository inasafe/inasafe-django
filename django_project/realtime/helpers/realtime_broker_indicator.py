# coding=utf-8
import pickle
import os
from datetime import datetime

import pytz
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.humanize.templatetags.humanize import naturaltime

from realtime.app_settings import REALTIME_BROKER_INTERVAL_RANGE
from realtime.helpers.base_indicator import Indicator, STATUS_HEALTHY, \
    STATUS_WARNING, STATUS_CRITICAL
from realtime.templatetags.realtime_extras import naturaltimedelta

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/17/16'


class RealtimeBrokerIndicator(Indicator):
    """An indicator to check the availability of Realtime Broker
    """

    def __init__(self):
        super(RealtimeBrokerIndicator, self).__init__()

        # load from JSON saved object if any
        django_root = settings.DJANGO_ROOT
        pickle_path = os.path.join(
            django_root, '.realtime_broker_indicator.pickle')
        self.pickle_path = pickle_path
        if os.path.exists(pickle_path):
            saved_data = pickle.load(open(pickle_path))
            self._value = saved_data.get('value')
            value = self._value
        else:
            min_time = datetime.fromtimestamp(0, tz=pytz.utc)
            self._value = min_time
            value = self._value

        healthy_range = REALTIME_BROKER_INTERVAL_RANGE['healthy']
        warning_range = REALTIME_BROKER_INTERVAL_RANGE['warning']

        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        connection_check_delta = now - value

        if connection_check_delta < healthy_range:
            self._status = STATUS_HEALTHY
        elif connection_check_delta < warning_range:
            self._status = STATUS_WARNING
        else:
            self._status = STATUS_CRITICAL

        self._healthy_range = healthy_range
        self._warning_range = warning_range
        self._label = _('Broker Connection Status')

    @Indicator.value.setter
    def value(self, val):
        if isinstance(val, datetime):
            val = val.astimezone(pytz.utc)
            self._value = val
            saved_data = {
                'value': val
            }
            pickle.dump(saved_data, open(self.pickle_path, 'w'))
        else:
            raise ValueError('Datetime value expected')

    def notes(self):
        available_notes = {
            STATUS_HEALTHY: _(
                'Status is considered in healthy state when the value is less'
                ' than %s') % (
                naturaltimedelta(self._healthy_range, clarity=2)
            ),
            STATUS_WARNING: _(
                'Status is considered in warning state when the value is less'
                ' than %s') % (
                naturaltimedelta(self._warning_range, clarity=2)
            ),
            STATUS_CRITICAL: _(
                'Status is considered in critical state when the value is '
                'greater than %s') % (
                naturaltimedelta(self._warning_range, clarity=2)
            )
        }
        return available_notes.get(self.status)

    def value_humanize(self):
        return naturaltime(self.value)
