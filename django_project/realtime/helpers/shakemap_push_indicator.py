# coding=utf-8
from datetime import datetime, timedelta
from django.contrib.humanize.templatetags.humanize import naturaltime

from django.utils.translation import ugettext as _
from django.db.models.aggregates import Max
import pytz
from realtime.app_settings import SHAKE_INTERVAL_MULTIPLIER
from realtime.helpers.base_indicator import Indicator, \
    average_shake_interval, STATUS_HEALTHY, STATUS_WARNING, STATUS_CRITICAL
from realtime.models.user_push import UserPush
from realtime.templatetags.realtime_extras import naturaltimedelta

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '04/09/15'


class ShakemapPushIndicator(Indicator):
    """An indicator class for recorded last Shakemap Push by a user.

    Shakemap Push is an action that describes when user is uploading raw
    shake data to InaSAFE Realtime processor.

    Shakemap Push is initiated by a shakemap provider (e.g. BMKG) and it
    tries to send raw Shakemap Data to be processed by Realtime processor.
    This push is done via sftp, btsync, or any other way and is detected
    by using inotify-tools. After it is detected, Realtime Processor send
    a request to Realtime REST server to indicate that a provider has sent
    new Shakemap. This request is recorded to know when was the last time
    a provider successfully send new shakemap.
    The indicator estimate the status of the process. If it is considered
    Critical (with estimation), then a shakemap push didn't happen after
    a considered average interval. Which means it probably indicates
    something happened that caused the shakemap didn't get sent.
    """

    def __init__(self):
        super(ShakemapPushIndicator, self).__init__()
        # get the last
        value = UserPush.objects.all().aggregate(
            Max('last_shakemap_push'))['last_shakemap_push__max']

        # assign default value
        min_time = datetime.fromtimestamp(0, tz=pytz.utc)
        if not value:
            value = min_time
        else:
            value = value.astimezone(pytz.utc)

        # calculate average shakemap push
        # average shakemap push is supposed to be average shake event interval
        # we will calculate the average from previous month
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        mean_interval, deviation = average_shake_interval(num_days=30)
        shakemap_push_delta = now - value

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

        if shakemap_push_delta < healthy_range:
            self._status = STATUS_HEALTHY
        elif shakemap_push_delta < warning_range:
            self._status = STATUS_WARNING
        else:
            self._status = STATUS_CRITICAL

        self._value = value
        self._mean_interval = mean_interval
        self._deviation = deviation
        self._healthy_range = healthy_range
        self._warning_range = warning_range

        self._label = _('Last Shakemap Push')

    def notes(self):
        available_notes = {
            STATUS_HEALTHY: _(
                'Status is considered in healthy state when the value is '
                'less than %(factor).2f times of deviation (%(deviation)s) '
                'from average '
                'intervals (%(interval)s) which is %(range)s') % {
                'factor': SHAKE_INTERVAL_MULTIPLIER['healthy'],
                'deviation': naturaltimedelta(self._deviation, clarity=2),
                'interval': naturaltimedelta(self._mean_interval, clarity=2),
                'range': naturaltimedelta(self._healthy_range, clarity=2)
            },
            STATUS_WARNING: _(
                'Status is considered in healthy state when the value is '
                'less than %(factor).2f times of deviation (%(deviation)) '
                'from average '
                'intervals (%(interval)s) which is %(range)s') % {
                'factor': SHAKE_INTERVAL_MULTIPLIER['warning'],
                'deviation': naturaltimedelta(self._deviation, clarity=2),
                'interval': naturaltimedelta(self._mean_interval, clarity=2),
                'range': naturaltimedelta(self._warning_range, clarity=2)
            },
            STATUS_CRITICAL: _(
                'Status is considered in healthy state when the value is '
                'less than %(factor).2f times of deviation (%(deviation)s) '
                'from average '
                'intervals (%(interval)s) which is %(range)s') % {
                'factor': SHAKE_INTERVAL_MULTIPLIER['warning'],
                'deviation': naturaltimedelta(self._deviation, clarity=2),
                'interval': naturaltimedelta(self._mean_interval, clarity=2),
                'range': naturaltimedelta(self._warning_range, clarity=2)
            }
        }
        return available_notes.get(self.status)

    def value_humanize(self):
        return naturaltime(self.value)
