# coding=utf-8
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext, loader
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from realtime.models.earthquake import Earthquake
from realtime.serializers.earthquake_serializer import (
    EarthquakeSerializer,
    EarthquakeGeoJsonSerializer
    )
from realtime.app_settings import LEAFLET_TILES
from realtime.forms import FilterForm
from realtime.tests.model_factories import EarthquakeFactory

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '19/06/15'


def index(request):
    """Index page of user map.

    :param request: A django request object.
    :type request: request

    :returns: Response will be a leaflet map page.
    :rtype: HttpResponse
    """

    if request.method == 'POST':
        pass
    else:
        form = FilterForm()

    leaflet_tiles = dict(
        url=LEAFLET_TILES[1],
        attribution=LEAFLET_TILES[2]
        )

    context = RequestContext(request)
    context['leaflet_tiles'] = leaflet_tiles
    return render_to_response(
            'realtime/index.html',
            {'form': form},
            context_instance=context
            )


def get_earthquakes(request):
    """Return a json document of earthquakes.

    :param request: A django request object.
    :type request: request

    :returns: JSON file of all events.
    :type: JSON.
    """
    if request.method == 'GET':

        # Get data:
        events = Earthquake.objects.all()
        context = {'events': events}
        events_json = loader.render_to_string(
            'realtime/events.json',
            context_instance=RequestContext(request, context))
        # Return Response
        return HttpResponse(events_json, content_type='application/json')
    else:
        raise Http404


def populate(request):
    """saves an earthquake to the db.(just for testing)

    :param request: A django request object.
    :type request: request
    """
    if request.method == 'GET':
        earthquake = EarthquakeFactory.create()
        earthquake.save()
        return index(request)


@api_view(['GET', 'POST'])
def earthquake_feature_list(request, format=None):
    """Get GEOJson representation of all events.

    :param request: A django request object.
    :type request: request

    :returns: GeoJSON file of all events.
    :type: GeoJSON.
    """
    if request.method == 'GET':
        earthquake = Earthquake.objects.all()
        serializer = EarthquakeGeoJsonSerializer(earthquake, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = EarthquakeGeoJsonSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def earthquake_list(request, format=None):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        earthquake = Earthquake.objects.all()
        serializer = EarthquakeSerializer(earthquake, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = EarthquakeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def earthquake_detail(request, shake_id, format=None):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        earthquake = Earthquake.objects.get(shake_id=shake_id)
    except Earthquake.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EarthquakeSerializer(earthquake)
        return Response(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = EarthquakeSerializer(earthquake, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        earthquake.delete()
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
