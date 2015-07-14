# coding=utf-8
from copy import deepcopy

from django.shortcuts import render_to_response
from django.template import RequestContext
from rest_framework import status, mixins
from rest_framework.filters import DjangoFilterBackend, SearchFilter, \
    OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response
from realtime.app_settings import LEAFLET_TILES
from realtime.forms import FilterForm
from realtime.filters.earthquake_filter import EarthquakeFilter
from realtime.models.earthquake import Earthquake, EarthquakeReport
from realtime.serializers.earthquake_serializer import EarthquakeSerializer, \
    EarthquakeReportSerializer, EarthquakeGeoJsonSerializer
from rest_framework_gis.filters import InBBoxFilter

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '19/06/15'


def index(request, iframe=False, server_side_filter=False):
    """Index page of realtime.

    :param request: A django request object.
    :type request: request

    :returns: Response will be a leaflet map page.
    :rtype: HttpResponse
    """

    if request.method == 'POST':
        pass
    else:
        form = FilterForm()

    if request.method == 'GET':
        if 'iframe' in request.GET:
            iframe = request.GET.get('iframe')
        if 'server_side_filter' in request.GET:
            server_side_filter = request.GET.get('server_side_filter')

    leaflet_tiles = dict(
        url=LEAFLET_TILES[1],
        attribution=LEAFLET_TILES[2]
        )

    context = RequestContext(request)
    context['leaflet_tiles'] = leaflet_tiles
    context['language'] = 'en'
    context['select_area_text'] = 'Select Area'
    context['remove_area_text'] = 'Remove Selection'
    context['select_current_zoom_text'] = 'Select area within current zoom'
    context['iframe'] = iframe
    return render_to_response(
        'realtime/index.html',
        {
            'form': form,
            'iframe': iframe,
            'server_side_filter': server_side_filter
        },
        context_instance=context)


def iframe_index(request):
    """Index page of realtime in iframe.

    :param request: A django request object.
    :type request: request

    :returns: Response will be a leaflet map page.
    :rtype: HttpResponse
    """
    return index(request, iframe=True)


class EarthquakeList(mixins.ListModelMixin, mixins.CreateModelMixin,
                     GenericAPIView):
    """
    Provides GET and POST requests to retrieve and save Earthquake models.

    ### Filters

    These are the available filters:

    * min_depth
    * max_depth
    * min_magnitude or minimum_magnitude
    * max_magnitude or maximum_magnitude
    * min_time or time_start
    * max_time or time_end
    * location_description
    * in_bbox filled with BBox String in the format SWLon,SWLat,NELon,NELat
    this is used as geographic box filter
    """

    queryset = Earthquake.objects.all()
    serializer_class = EarthquakeSerializer
    parser_classes = [JSONParser, FormParser]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,
                       InBBoxFilter)
    bbox_filter_field = 'location'
    bbox_filter_include_overlapping = True
    filter_fields = ('depth', 'magnitude', 'shake_id')
    filter_class = EarthquakeFilter
    search_fields = ('location_description', )
    ordering = ('shake_id', )
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

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
    parser_classes = (JSONParser, FormParser, )
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

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
    Provides GET and POST requests to retrieve and save Earthquake
    Report models.

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
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

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
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

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


class EarthquakeFeatureList(EarthquakeList):
    """
    Provides GET requests to retrieve Earthquake models
    in a GEOJSON format.

    ### Filters

    These are the available filters:

    * min_depth
    * max_depth
    * min_magnitude or minimum_magnitude
    * max_magnitude or maximum_magnitude
    * min_time or time_start
    * max_time or time_end
    * location_description
    * in_bbox filled with BBox String in the format SWLon,SWLat,NELon,NELat
    this is used as geographic box filter
    """
    serializer_class = EarthquakeGeoJsonSerializer
    pagination_class = None
