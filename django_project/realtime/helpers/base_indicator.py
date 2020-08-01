# coding=utf-8
from builtins import range
from builtins import object
from datetime import datetime, timedelta
from math import isnan
from django.utils.translation import ugettext as _
import numpy
import pytz
from realtime.models.earthquake import Earthquake

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '04/09/15'


STATUS_HEALTHY = 'Healthy'
STATUS_WARNING = 'Warning'
STATUS_CRITICAL = 'Critical'


class Indicator(object):
    """An abstract class of indicators.

    This class should provide a way to generate indicator info to know that
    realtime is running fine.
    """

    def __init__(self):
        self._value = None
        self._label = None
        self._status = None

    @property
    def value(self):
        return self._value

    @property
    def label(self):
        return self._label

    @property
    def status(self):
        return self._status

    def value_humanize(self):
        raise NotImplementedError()

    def notes(self):
        raise NotImplementedError()

    def is_healthy(self):
        return self.status == STATUS_HEALTHY

    def is_warning(self):
        return self.status == STATUS_WARNING

    def is_critical(self):
        return self.status == STATUS_CRITICAL

    def status_text(self):
        if self.status == STATUS_HEALTHY:
            return _('Healthy')
        elif self.status == STATUS_WARNING:
            return _('Warning')
        elif self.status == STATUS_CRITICAL:
            return _('Critical')
        else:
            return _('Not Available')


# this line onward will contains helpers method
def average_shake_interval(num_days=30):
    """Calculates average interval between shake events.

    It is calculated in the span of previous 30 days

    :param num_days: Number of previous days the function will calculate
    :type num_days: int

    :return: tuple of mean interval and standard deviation of shake events
    :rtype: tuple
    """
    last_span = datetime.utcnow() - timedelta(days=num_days)
    last_span.replace(tzinfo=pytz.utc)
    shakes = Earthquake.objects.filter(time__gte=last_span)
    intervals = []
    for i in range(1, len(shakes)):
        prev_shake = shakes[i - 1]
        shake = shakes[i]
        intervals.append(shake.time - prev_shake.time)

    # using numpy to calculate mean
    intervals = numpy.array([i.total_seconds() for i in intervals])
    mean_interval = numpy.mean(intervals)
    if isinstance(mean_interval, float) and isnan(mean_interval):
        mean_interval = 0

    # using numpy to calculate std
    deviation = numpy.std(intervals)
    if isinstance(deviation, float) and isnan(deviation):
        deviation = 0
    return timedelta(seconds=mean_interval), timedelta(seconds=deviation)
