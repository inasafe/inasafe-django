# coding=utf-8
from datetime import datetime, timedelta
from django.contrib.humanize.templatetags.humanize import naturaltime

from django.utils.translation import ugettext as _
from django.db.models.aggregates import Max
import pytz
from realtime.app_settings import SHAKE_INTERVAL_MULTIPLIER
from realtime.helpers.base_indicator import Indicator, \
    average_shake_interval, STATUS_HEALTHY, STATUS_WARNING, STATUS_CRITICAL
from realtime.models.earthquake import Earthquake
from realtime.templatetags.realtime_extras import naturaltimedelta

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '04/09/15'


class ShakeEventIndicator(Indicator):
    """An indicator class for recorded last Shakemap Event by a user.

    Shakemap Event is a shake event recorded in Realtime REST server.

    Shake will happen at *somewhat* regular interval. So, usually we
    will expect that another shake will happen after an average
    interval. If it doesn't happen or the indicator reached an estimate
    of critical state, it probably means that somehow Realtime Processor
    can't send shakemap event to Realtime REST server, or perhaps there
    were no shake at all.
    """

    def __init__(self):
        super(ShakeEventIndicator, self).__init__()
        # get the last
        value = Earthquake.objects.all().aggregate(
            Max('time'))['time__max']

        # assign default value
        min_time = datetime.fromtimestamp(0, tz=pytz.utc)
        if not value:
            value = min_time
        else:
            value = value.astimezone(pytz.utc)

        # calculate average shakemap event interval
        # we will calculate the average from previous month
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        mean_interval, deviation = average_shake_interval(num_days=30)
        shake_event_delta = now - value

        healthy_seconds = (
            mean_interval.total_seconds() +
            deviation.total_seconds() * SHAKE_INTERVAL_MULTIPLIER['healthy']
        )
        warning_seconds = (
            mean_interval.total_seconds() +
            deviation.total_seconds() * SHAKE_INTERVAL_MULTIPLIER['warning']
        )
        healthy_range = timedelta(
            seconds=healthy_seconds)
        warning_range = timedelta(
            seconds=warning_seconds)

        if shake_event_delta < healthy_range:
            self._status = STATUS_HEALTHY
        elif shake_event_delta < warning_range:
            self._status = STATUS_WARNING
        else:
            self._status = STATUS_CRITICAL

        self._value = value
        self._mean_interval = mean_interval
        self._deviation = deviation
        self._healthy_range = healthy_range
        self._warning_range = warning_range

        self._label = _('Last Shake Event')

    def notes(self):
        available_notes = {
            STATUS_HEALTHY: _(
                'Status is considered in healthy state when the value is '
                'less than %.2f times of deviation (%s) from average '
                'intervals (%s) which is %s') % (
                SHAKE_INTERVAL_MULTIPLIER['healthy'],
                naturaltimedelta(self._deviation, clarity=2),
                naturaltimedelta(self._mean_interval, clarity=2),
                naturaltimedelta(self._healthy_range, clarity=2)
            ),
            STATUS_WARNING: _(
                'Status is considered in healthy state when the value is '
                'less than %.2f times of deviation (%s) from average '
                'intervals (%s) which is %s') % (
                SHAKE_INTERVAL_MULTIPLIER['warning'],
                naturaltimedelta(self._deviation, clarity=2),
                naturaltimedelta(self._mean_interval, clarity=2),
                naturaltimedelta(self._warning_range, clarity=2)
            ),
            STATUS_CRITICAL: _(
                'Status is considered in healthy state when the value is '
                'less than %.2f times of deviation (%s) from average '
                'intervals (%s) which is %s') % (
                SHAKE_INTERVAL_MULTIPLIER['warning'],
                naturaltimedelta(self._deviation, clarity=2),
                naturaltimedelta(self._mean_interval, clarity=2),
                naturaltimedelta(self._warning_range, clarity=2)
            )
        }
        return available_notes.get(self.status)

    def value_humanize(self):
        return naturaltime(self.value)
