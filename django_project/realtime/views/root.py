# coding=utf-8
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '24/06/15'


@api_view(('GET',))
def api_root(request, format=None, **kwargs):
    kwargs['request'] = request
    kwargs['format'] = format
    return Response({
        'model_list': {
            'earthquakes': reverse('realtime:earthquake_list', **kwargs),
            'earthquake-reports': reverse(
                'realtime:earthquake_report_list', **kwargs),
            'earthquake-feature-list': reverse(
                'realtime:earthquake_feature_list', **kwargs),
            'floods': reverse('realtime:flood_list', **kwargs)
        }
    })


def is_logged_in(request):
    data = {
        'is_logged_in': request.user.is_authenticated()
    }
    return JsonResponse(data=data)
