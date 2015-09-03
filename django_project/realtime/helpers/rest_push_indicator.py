# coding=utf-8
from django.contrib.humanize.templatetags.humanize import naturaltime
import pytz
from datetime import datetime
from django.utils.translation import ugettext as _
from django.db.models.aggregates import Max
from realtime.app_settings import REST_INTERVAL_RANGE
from realtime.helpers.base_indicator import Indicator, STATUS_HEALTHY, \
    STATUS_WARNING, STATUS_CRITICAL
from realtime.models.user_push import UserPush
from realtime.templatetags.realtime_extras import naturaltimedelta
from user_map.models.user import User

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '04/09/15'


class RESTPushIndicator(Indicator):
    """An Indicator class for how healthy the REST Push operate

    A REST Push is an event of sending a shakemap info from
    Realtime Processor to Realtime REST server.

    Realtime REST push is sent on a regular interval because it is
    initiated by a cronjob running in Realtime Processor. So, if
    for a fixed interval a REST push didn't happen. This would
    definitely indicate that connection between Processor and REST
    server is broken.
    """

    def __init__(self):
        super(RESTPushIndicator, self).__init__()

        value = UserPush.objects.all().aggregate(
            Max('last_rest_push'))['last_rest_push__max']

        # assign default value
        min_time = datetime.fromtimestamp(0, tz=pytz.utc)
        if not value:
            value = min_time
        else:
            value = value.astimezone(pytz.utc)

        healthy_range = REST_INTERVAL_RANGE['healthy']
        warning_range = REST_INTERVAL_RANGE['warning']

        # for last rest push, because cronjob always process the last
        # shake map every 1 minute, we specify it using fixed interval

        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        rest_push_delta = now - value

        if rest_push_delta < healthy_range:
            self._status = STATUS_HEALTHY
        elif rest_push_delta < warning_range:
            self._status = STATUS_WARNING
        else:
            self._status = STATUS_CRITICAL

        self._value = value
        self._healthy_range = healthy_range
        self._warning_range = warning_range

        self._label = _('Last REST Push')

    def notes(self):
        available_notes = {
            STATUS_HEALTHY: _(
                'Status is considered in healthy state when the value is less'
                ' than %s') % (
                naturaltimedelta(self._healthy_range)
            ),
            STATUS_WARNING: _(
                'Status is considered in warning state when the value is less'
                ' than %s') % (
                naturaltimedelta(self._warning_range)
            ),
            STATUS_CRITICAL: _(
                'Status is considered in critical state when the value is greater'
                ' than %s') % (
                naturaltimedelta(self._warning_range)
            )
        }
        return available_notes.get(self.status)

    def value_humanize(self):
        return naturaltime(self.value)


def track_rest_push(request):
    # track the last successfull post/put from user
    if request.user.is_authenticated():
        user = User.objects.get(email=request.user.email)
        try:
            user_push = UserPush.objects.get(user=user)
        except UserPush.DoesNotExist:
            user_push = UserPush.objects.create(user=user)
            user_push.save()

        # update info
        user_push.last_rest_push = datetime.utcnow()
        user_push.save()
