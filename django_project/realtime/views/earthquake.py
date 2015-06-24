# coding=utf-8
from copy import deepcopy

from realtime.filters.earthquake_filter import EarthquakeFilter
from rest_framework.filters import DjangoFilterBackend, SearchFilter, \
    OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import status, mixins
from realtime.models.earthquake import Earthquake, EarthquakeReport
from realtime.serializers.earthquake_serializer import EarthquakeSerializer, \
    EarthquakeReportSerializer

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '19/06/15'


class EarthquakeList(mixins.ListModelMixin, mixins.CreateModelMixin,
                     GenericAPIView):
    """
    Provides GET and POST requests to retrieve and save Earthquake models.

    ### Filters

    These are the available filters:

    * depth_min
    * depth_max
    * magnitude_min
    * magnitude_max
    * location_description
    """

    queryset = Earthquake.objects.all()
    serializer_class = EarthquakeSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('depth', 'magnitude', 'shake_id')
    filter_class = EarthquakeFilter
    search_fields = ('location_description', )
    ordering = ('shake_id', )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class EarthquakeDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin, GenericAPIView):
    """
    Provides GET, PUT, and DELETE requests to retrieve, update and delete
    Earthquake models.
    """
    queryset = Earthquake.objects.all()
    serializer_class = EarthquakeSerializer
    lookup_field = 'shake_id'
    parser_classes = (JSONParser, FormParser, MultiPartParser, )

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class EarthquakeReportList(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.CreateModelMixin,
                           GenericAPIView):
    """
    Provides GET and POST requests to retrieve and save Earthquake Report models.

    ### Filters

    These are the available filters:

    * earthquake__shake_id
    * language
    """
    queryset = EarthquakeReport.objects.all()
    serializer_class = EarthquakeReportSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('earthquake__shake_id', 'language', )
    search_fields = ('earthquake__shake_id', 'language', )
    ordering_fields = ('earthquake__shake_id', 'language', )
    ordering = ('earthquake__shake_id', )

    def get(self, request, shake_id=None, *args, **kwargs):
        try:
            if shake_id:
                instances = EarthquakeReport.objects.filter(
                    earthquake__shake_id=shake_id)
                page = self.paginate_queryset(instances)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

                serializer = self.get_serializer(instances, many=True)
                return Response(serializer.data)
            else:
                return self.list(request, *args, **kwargs)
        except EarthquakeReport.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            shake_id = kwargs.get('shake_id') or data.get('shake_id')
            data['shake_id'] = shake_id
            earthquake = Earthquake.objects.get(shake_id=shake_id)
            report = EarthquakeReport.objects.filter(
                earthquake=earthquake, language=data['language'])
        except Earthquake.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if report:
            # cannot post report if it is already exists
            serializer = EarthquakeReportSerializer(report[0])
            return Response(
                serializer.data, status=status.HTTP_400_BAD_REQUEST)

        serializer = EarthquakeReportSerializer(data=data)

        if serializer.is_valid():
            serializer.validated_data['earthquake'] = earthquake
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EarthquakeReportDetail(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.DestroyModelMixin, GenericAPIView):
    """
    Provides GET, PUT, and DELETE requests to retrieve, update and delete
    Earthquake Report models.
    """
    queryset = EarthquakeReport.objects.all()
    serializer_class = EarthquakeReportSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser, )

    def get(self, request, shake_id=None, language=None, *args, **kwargs):
        try:
            if shake_id and language:
                instance = EarthquakeReport.objects.get(
                    earthquake__shake_id=shake_id,
                    language=language)
                serializer = self.get_serializer(instance)
                return Response(serializer.data)
            elif shake_id:
                return self.list(request, *args, **kwargs)
        except EarthquakeReport.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, shake_id=None, language=None):
        data = request.data
        try:
            if shake_id:
                data['shake_id'] = shake_id
                report = EarthquakeReport.objects.get(
                    earthquake__shake_id=shake_id, language=language)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except EarthquakeReport.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # delete previous files
        new_report = deepcopy(report)
        new_report.pk = None
        report.delete()
        serializer = EarthquakeReportSerializer(new_report, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, shake_id, language):
        try:
            report = EarthquakeReport.objects.get(
                earthquake__shake_id=shake_id, language=language)
        except EarthquakeReport.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
