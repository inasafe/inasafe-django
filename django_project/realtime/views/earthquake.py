# coding=utf-8
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from realtime.models.earthquake import Earthquake
from realtime.serializers.earthquake_serializer import EarthquakeSerializer

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '19/06/15'


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
