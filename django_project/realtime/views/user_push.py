# coding=utf-8
import pytz
from datetime import datetime

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import translation
from django.http.response import JsonResponse
from realtime.app_settings import LANGUAGE_LIST
from realtime.helpers.realtime_broker_indicator import RealtimeBrokerIndicator
from realtime.helpers.shake_event_indicator import ShakeEventIndicator
from realtime.helpers.shakemap_push_indicator import ShakemapPushIndicator
from realtime.models.user_push import UserPush
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
        # calculate from utc
        date_format = '%Y-%m-%d %H:%M:%S'
        timestamp = request.POST['timestamp']
        if timestamp:
            time = datetime.strptime(
                timestamp, date_format).replace(tzinfo=pytz.utc)
        else:
            time = datetime.utcnow()
        user_push.last_shakemap_push = time.replace(tzinfo=pytz.utc)
        user_push.save()
        retval['success'] = True
        return JsonResponse(retval)
    else:
        retval['success'] = False
        return JsonResponse(retval)


def indicator(request):
    """Return a view to show the healthiness of Realtime system

    :param request: A django request object.
    :type request: request

    :returns: Response will be a leaflet map page.
    :rtype: HttpResponse
    """
    # FIXME: comment this out for now
    # fix this after it is clear who can access this page
    # if not request.user.is_authenticated():
    #    return HttpResponseNotAllowed()

    language_code = 'en'
    if request.method == 'GET':
        if 'lang' in request.GET:
            language_code = request.GET.get('lang')

    shakemap_push_indicator = ShakemapPushIndicator()
    shake_event_indicator = ShakeEventIndicator()
    # rest_push_indicator = RESTPushIndicator()
    realtime_broker_indicator = RealtimeBrokerIndicator()

    context = RequestContext(request)
    selected_language = {
        'id': 'en',
        'name': 'English'
    }
    for lang in LANGUAGE_LIST:
        if lang['id'] == language_code:
            selected_language = lang

    language_list = [
        lang for lang in LANGUAGE_LIST if not lang['id'] == language_code]
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
            'indicators': [
                shakemap_push_indicator,
                shake_event_indicator,
                realtime_broker_indicator
            ]
        },
        context_instance=context)


def realtime_rest_users(request):
    users = UserPush.objects.all()
    date_format = '%Y-%m-%d %H:%M:%S %Z'
    user_json = [
        {
            'username': u.user.get_username(),
            'email': u.user.email,
            'last_shakemap_push': u.last_shakemap_push.strftime(
                date_format),
            'last_rest_push': u.last_rest_push.strftime(date_format)
        }
        for u in users
    ]
    return JsonResponse({
        'users': user_json
    })
