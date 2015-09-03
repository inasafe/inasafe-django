# coding=utf-8
from math import isnan
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import translation
import pytz
import numpy
from django.utils.translation import ugettext as _
from datetime import datetime, timedelta
from django.db.models.aggregates import Max
from django.http.response import JsonResponse, HttpResponseNotAllowed
from realtime.app_settings import SHAKE_INTERVAL_MULTIPLIER, \
    REST_INTERVAL_RANGE, LANGUAGE_LIST
from realtime.models.earthquake import Earthquake
from realtime.models.user_push import UserPush
from realtime.templatetags.realtime_extras import naturaltimedelta
from user_map.models.user import User

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '02/09/15'


def notify_shakemap_push(request):
    """Notify Realtime that a shakemap push is happening in the processor


    :param request: A django request object. Should be a POST request
    :type request: request

    :returns: Response will be a json with structure { 'success': bool }.
    :rtype: HttpResponse
    """

    retval = {}
    # the call should be authenticated
    # and make sure it is a post request (to follow REST principle)
    if request.user.is_authenticated() and request.method == 'POST':
        user = User.objects.get(email=request.user.email)
        try:
            user_push = UserPush.objects.get(user=user)
        except UserPush.DoesNotExist:
            user_push = UserPush.objects.create(user=user)
            user_push.save()

        # update info
        # get shakemap timestamp
        date_format = '%Y-%m-%d %H:%M:%S %Z'
        timestamp = request.POST['timestamp']
        if timestamp:
            time = datetime.strptime(
                timestamp, date_format).astimezone(pytz.utc)
        else:
            time = datetime.utcnow()
        user_push.last_shakemap_push = time.replace(tzinfo=pytz.utc)
        user_push.save()
        retval['success'] = True
        return JsonResponse(retval)
    else:
        return HttpResponseNotAllowed()


def indicator(request):
    """Return a view to show the healthiness of Realtime system

    :param request: A django request object.
    :type request: request

    :returns: Response will be a leaflet map page.
    :rtype: HttpResponse
    """
    if not request.user.is_authenticated():
        return HttpResponseNotAllowed()

    language_code = 'en'
    if request.method == 'GET':
        if 'lang' in request.GET:
            language_code = request.GET.get('lang')

    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    last_shakemap_push = {}
    last_rest_push = {}
    last_shake_event = {}

    last_shakemap_push['value'] = UserPush.objects.all().aggregate(
        Max('last_shakemap_push'))['last_shakemap_push__max']
    last_rest_push['value'] = UserPush.objects.all().aggregate(
        Max('last_rest_push'))['last_rest_push__max']
    last_shake_event['value'] = Earthquake.objects.all().aggregate(
        Max('time'))['time__max']

    # assign default value
    min_time = datetime.fromtimestamp(0, tz=pytz.utc)
    if not last_shakemap_push['value']:
        last_shakemap_push['value'] = min_time
    else:
        last_shakemap_push['value'] = last_shakemap_push['value']\
            .astimezone(pytz.utc)

    if not last_rest_push['value']:
        last_rest_push['value'] = min_time
    else:
        last_rest_push['value'] = last_rest_push['value']\
            .astimezone(pytz.utc)

    if not last_shake_event['value']:
        last_shake_event['value'] = min_time
    else:
        last_shake_event['value'] = last_shake_event['value']\
            .astimezone(pytz.utc)

    # calculate average shakemap push
    # average shakemap push is supposed to be average shake event interval
    # we will calculate the average from previous month
    last_month = datetime.utcnow() - timedelta(days=30)
    last_month.replace(tzinfo=pytz.utc)
    shakes = Earthquake.objects.filter(time__gte=last_month)
    intervals = []
    for i in range(1, len(shakes)):
        prev_shake = shakes[i-1]
        shake = shakes[i]
        intervals.append(shake.time - prev_shake.time)

    # using numpy to calculate mean
    intervals = numpy.array([numpy.timedelta64(i) for i in intervals])
    mean_interval = numpy.mean(intervals).astype(timedelta)
    if isnan(mean_interval):
        mean_interval = timedelta(seconds=0)
    shakemap_push_delta = now - last_shakemap_push['value']

    success_range = timedelta(
        seconds=mean_interval.seconds *
        SHAKE_INTERVAL_MULTIPLIER['success'])
    warning_range = timedelta(
        seconds=mean_interval.seconds *
        SHAKE_INTERVAL_MULTIPLIER['warning'])
    if shakemap_push_delta < success_range:
        last_shakemap_push['status'] = 'success'
        last_shakemap_push['status_text'] = _('Healthy')
        last_shakemap_push['notes'] = _(
            'Status is considered in healthy state when the value is less '
            'than %.2f times average interval of %s which is %s') % (
            SHAKE_INTERVAL_MULTIPLIER['success'],
            naturaltimedelta(mean_interval),
            naturaltimedelta(success_range)
        )
        last_shake_event['status'] = 'success'
        last_shake_event['status_text'] = _('Healthy')
        last_shake_event['notes'] = _(
            'Status is considered in healthy state when the value is less '
            'than %.2f times average interval of %s which is %s') % (
            SHAKE_INTERVAL_MULTIPLIER['success'],
            naturaltimedelta(mean_interval),
            naturaltimedelta(success_range)
        )
    elif shakemap_push_delta < warning_range:
        last_shakemap_push['status'] = 'warning'
        last_shakemap_push['status_text'] = _('Warning')
        last_shakemap_push['notes'] = _(
            'Status is considered in warning state when the value is less '
            'than %.2f times average interval of %s which is %s') % (
            SHAKE_INTERVAL_MULTIPLIER['warning'],
            naturaltimedelta(mean_interval),
            naturaltimedelta(warning_range)
        )
        last_shake_event['status'] = 'warning'
        last_shake_event['status_text'] = _('Warning')
        last_shake_event['notes'] = _(
            'Status is considered in warning state when the value is less '
            'than %.2f times average interval of %s which is %s') % (
            SHAKE_INTERVAL_MULTIPLIER['warning'],
            naturaltimedelta(mean_interval),
            naturaltimedelta(warning_range)
        )
    else:
        last_shakemap_push['status'] = 'danger'
        last_shakemap_push['status_text'] = _('Critical')
        last_shakemap_push['notes'] = _(
            'Status is considered in critical state when the value is greater'
            ' than %.2f times average interval of %s which is %s') % (
            SHAKE_INTERVAL_MULTIPLIER['warning'],
            naturaltimedelta(mean_interval),
            naturaltimedelta(warning_range)
        )
        last_shake_event['status'] = 'danger'
        last_shake_event['status_text'] = _('Critical')
        last_shake_event['notes'] = _(
            'Status is considered in critical state when the value is greater'
            ' than %.2f times average interval of %s which is %s') % (
            SHAKE_INTERVAL_MULTIPLIER['warning'],
            naturaltimedelta(mean_interval),
            naturaltimedelta(warning_range)
        )

    success_range = REST_INTERVAL_RANGE['success']
    warning_range = REST_INTERVAL_RANGE['warning']

    # for last rest push, because cronjob always process the last shake map
    # every 1 minute, we specify it using fixed interval
    rest_push_delta = now - last_rest_push['value']
    if rest_push_delta < success_range:
        last_rest_push['status'] = 'success'
        last_rest_push['status_text'] = _('Healthy')
        last_rest_push['notes'] = _(
            'Status is considered in healthy state when the value is less'
            ' than %s') % (
            naturaltimedelta(success_range)
        )
    elif rest_push_delta < warning_range:
        last_rest_push['status'] = 'warning'
        last_rest_push['status_text'] = _('Warning')
        last_rest_push['notes'] = _(
            'Status is considered in warning state when the value is less'
            ' than %s') % (
            naturaltimedelta(warning_range)
        )
    else:
        last_rest_push['status'] = 'danger'
        last_rest_push['status_text'] = _('Critical')
        last_rest_push['notes'] = _(
            'Status is considered in critical state when the value is greater'
            ' than %s') % (
            naturaltimedelta(warning_range)
        )

    context = RequestContext(request)
    selected_language = {
        'id': 'en',
        'name': 'English'
    }
    for l in LANGUAGE_LIST:
        if l['id'] == language_code:
            selected_language = l

    language_list = [l for l in LANGUAGE_LIST if not l['id'] == language_code]
    context['language'] = {
        'selected_language': selected_language,
        'language_list': language_list,
    }
    translation.activate(selected_language['id'])
    request.session[translation.LANGUAGE_SESSION_KEY] = \
        selected_language['id']

    return render_to_response(
        'realtime/indicator.html',
        {
            'last_shakemap_push': last_shakemap_push,
            'last_rest_push': last_rest_push,
            'last_shake_event': last_shake_event
        },
        context_instance=context)


def realtime_rest_users(request):
    if request.user.is_authenticated():
        users = UserPush.objects.all()
        json_response = [
            {
                'username': u.user.get_username(),
                'email': u.user.email,
                'last_shakemap_push': u.last_shakemap_push,
                'last_rest_push': u.last_rest_push
            }
            for u in users
        ]
        return JsonResponse(json_response)
    else:
        return HttpResponseNotAllowed()
