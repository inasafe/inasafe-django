# coding=utf-8
from copy import deepcopy

from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from realtime.models.earthquake import Earthquake, EarthquakeReport
from realtime.serializers.earthquake_serializer import EarthquakeSerializer, \
    EarthquakeReportSerializer

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '19/06/15'


@api_view(['GET', 'POST'])
def earthquake_list(request, format=None):
    """Earthquake list.
    """
    if request.method == 'GET':
        earthquake = Earthquake.objects.all()
        serializer = EarthquakeSerializer(earthquake, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data
        if isinstance(data, list):
            serializer = EarthquakeSerializer(data=data, many=True)
        else:
            serializer = EarthquakeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def earthquake_detail(request, shake_id, format=None):
    """Earthquake details.
    """
    try:
        earthquake = Earthquake.objects.get(shake_id=shake_id)
    except Earthquake.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EarthquakeSerializer(earthquake)
        return Response(serializer.data)

    elif request.method == 'PUT':
        data = request.data
        serializer = EarthquakeSerializer(earthquake, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        earthquake.delete()
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def earthquake_report_list(request, shake_id, format=None):
    """Earthquake report list.
    """
    try:
        earthquake = Earthquake.objects.get(shake_id=shake_id)
    except Earthquake.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        reports = EarthquakeReport.objects.filter(earthquake=earthquake)
        serializer = EarthquakeReportSerializer(reports, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data
        if isinstance(data, list):
            serializer = EarthquakeReportSerializer(data=data, many=True)
        else:
            serializer = EarthquakeReportSerializer(data=data)
        if serializer.is_valid():
            if isinstance(serializer.validated_data, list):
                for d in serializer.validated_data:
                    d['earthquake'] = earthquake
            else:
                serializer.validated_data['earthquake'] = earthquake
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def earthquake_report_detail(request, shake_id, language, format=None):
    """Earthquake report details.
    """
    try:
        report = EarthquakeReport.objects.get(
            earthquake__shake_id=shake_id, language=language)
    except EarthquakeReport.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EarthquakeReportSerializer(report)
        return Response(serializer.data)

    elif request.method == 'PUT':
        data = request.data
        # delete previous files
        new_report = deepcopy(report)
        new_report.pk = None
        report.delete()
        serializer = EarthquakeReportSerializer(new_report, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        report.delete()
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
