# coding=utf-8
import json
import logging

from datetime import datetime, timedelta
from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.db.models.aggregates import Count
from django.db.models import Q
from django.db.utils import IntegrityError
from django.http.response import JsonResponse, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import translation
from django.utils.translation import ugettext as _
from rest_framework import mixins, status
from rest_framework.filters import DjangoFilterBackend, SearchFilter, \
    OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response

from realtime.app_settings import (
    LEAFLET_TILES, LANGUAGE_LIST, MAPQUEST_MAP_KEY)
from realtime.forms.flood import FilterForm
from realtime.models.flood import Flood, FloodReport, Boundary, \
    FloodEventBoundary
from realtime.serializers.flood_serializer import FloodSerializer, \
    FloodReportSerializer

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '11/26/15'


LOGGER = logging.getLogger(__name__)


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

    language_code = 'en'
    if request.method == 'GET':
        if 'iframe' in request.GET:
            iframe = request.GET.get('iframe')
        if 'server_side_filter' in request.GET:
            server_side_filter = request.GET.get('server_side_filter')
        if 'lang' in request.GET:
            language_code = request.GET.get('lang')

    leaflet_tiles = []
    for i in range(0, len(LEAFLET_TILES[1])):
        leaflet_tiles.append(
            dict(
                name=LEAFLET_TILES[0][i],
                url=LEAFLET_TILES[1][i],
                subdomains=LEAFLET_TILES[2][i],
                attribution=LEAFLET_TILES[3][i]
            )
        )

    context = RequestContext(request)
    context['leaflet_tiles'] = leaflet_tiles
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
    context['select_area_text'] = _('Select Area')
    context['remove_area_text'] = _('Remove Selection')
    context['select_current_zoom_text'] = _('Select area within current zoom')
    context['iframe'] = iframe
    context['mapquest_key'] = MAPQUEST_MAP_KEY
    return render_to_response(
        'realtime/flood/index.html',
        {
            'form': form,
            'iframe': iframe,
            'server_side_filter': server_side_filter
        },
        context_instance=context)


class FloodList(mixins.ListModelMixin, mixins.CreateModelMixin,
                GenericAPIView):
    """Views for Flood models."""

    queryset = Flood.objects.all()
    serializer_class = FloodSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('event_id', 'interval')
    search_fields = ('event_id', )
    ordering = ('event_id', )
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        retval = self.create(request, *args, **kwargs)
        return retval


class FloodDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin, GenericAPIView):
    queryset = Flood.objects.all()
    serializer_class = FloodSerializer
    lookup_field = 'event_id'
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        try:
            event_id = request.data['event_id']
            if event_id:
                event = Flood.objects.get(event_id=event_id)
                event.hazard_layer.delete()
                event.impact_layer.delete()
                retval = self.update(request, partial=True, *args, **kwargs)
                return retval
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            LOGGER.warning(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class FloodReportList(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      GenericAPIView):

    queryset = FloodReport.objects.all()
    serializer_class = FloodReportSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('flood__event_id', 'language')
    search_fields = ('flood__event_id', 'language')
    ordering_fields = ('flood__event_id', 'language')
    ordering = ('flood__event_id', )
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

    def get(self, request, event_id=None, *args, **kwargs):
        try:
            if event_id:
                instances = FloodReport.objects.filter(
                    flood__event_id=event_id)
                page = self.paginate_queryset(instances)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

                serializer = self.get_serializer(instances, many=True)
                return Response(serializer.data)
            else:
                return self.list(request, *args, **kwargs)
        except FloodReport.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            event_id = kwargs.get('event_id') or data.get('event_id')
            data['event_id'] = event_id
            flood = Flood.objects.get(event_id=event_id)
            report = FloodReport.objects.filter(
                flood=flood, language=data['language'])
        except Flood.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if report:
            # cannot post report if it is already exists
            serializer = FloodReportSerializer(report[0])
            return Response(
                serializer.data, status=status.HTTP_400_BAD_REQUEST)

        serializer = FloodReportSerializer(data=data, partial=True)

        if serializer.is_valid():
            serializer.validated_data['flood'] = flood
            try:
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            except (ValidationError, IntegrityError) as e:
                # This happens when simultaneuously two conn trying to save
                # the same unique_together fields (earthquake, language)
                # Should warn this to sentry
                LOGGER.warning(e.message)
                return Response(
                    serializer.errors,
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FloodReportDetail(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, GenericAPIView):

    queryset = FloodReport.objects.all()
    serializer_class = FloodReportSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser, )
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

    def get(self, request, event_id=None, language=None, *args, **kwargs):
        try:
            if event_id and language:
                instance = FloodReport.objects.get(
                    flood__event_id=event_id,
                    language=language)
                serializer = self.get_serializer(instance)
                return Response(serializer.data)
            elif event_id:
                return self.list(request, *args, **kwargs)
        except FloodReport.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except MultipleObjectsReturned as e:
            # this should not happen.
            # But in case it is happening, returned the last object, but still
            # log the error to sentry
            LOGGER.warning(e.message)
            instance = FloodReport.objects.filter(
                flood__event_id=event_id,
                language=language).last()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

    def put(self, request, event_id=None, language=None):
        data = request.data
        try:
            if event_id:
                data['event_id'] = event_id
                report = FloodReport.objects.get(
                    flood__event_id=event_id, language=language)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except FloodReport.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # delete previous files
        report.impact_map.delete()
        report.impact_report.delete()
        serializer = FloodReportSerializer(report, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, event_id, language):
        try:
            report = FloodReport.objects.get(
                flood__event_id=event_id, language=language)
        except FloodReport.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FloodEventList(FloodList):
    # only retrieve for 6 interval hours
    serializer_class = FloodSerializer
    pagination_class = None

    def get_queryset(self):
        """Return only 6-interval hours.

        :return:
        """
        # this interval is specific for Jakarta (GMT+07)
        # it will show up as 6 hourly flood data from 00:00
        query = (
            Q(time__hour=23) | Q(time__hour=5) |
            Q(time__hour=11) | Q(time__hour=17))
        return Flood.objects.filter(query)


def flood_event_features(request, event_id):
    try:
        flood = Flood.objects.get(event_id=event_id)
        # build feature layer
        features = []
        for b in flood.flooded_boundaries.filter(boundary_alias__osm_level=8):
            event_data = b.flood_event.get(flood=flood)
            if event_data.hazard_data > 0:
                feat = {
                    'id': b.upstream_id,
                    'type': 'Feature',
                    'geometry': json.loads(b.geometry.geojson),
                    'properties': {
                        'event_id': flood.event_id,
                        'name': b.name,
                        'parent_name': b.parent.name,
                        'hazard_data': event_data.hazard_data
                    }
                }
                features.append(feat)

        feature_collection = {
            'type': 'FeatureCollection',
            'features': features
        }

        return JsonResponse(feature_collection)
    except:
        return HttpResponseServerError()


def impact_event_features(request, event_id):
    flood = Flood.objects.get(event_id=event_id)
    # build feature layer
    features = []
    for b in flood.impact_event.all():
        if b.hazard_class > 2:
            feat = {
                'id': b.id,
                'type': 'Feature',
                'geometry': json.loads(b.geometry.geojson),
                'properties': {
                    'event_id': flood.event_id,
                    'parent_boundary_name': b.parent_boundary.name,
                    'hazard_class': b.hazard_class,
                    'people_affected': b.population_affected
                }
            }
            features.append(feat)

    feature_collection = {
        'type': 'FeatureCollection',
        'features': features
    }

    return JsonResponse(feature_collection)


def rw_flood_frequency(request, hazard_levels_string=None):
    hazard_level = [1, 2, 3, 4]
    if hazard_levels_string:
        hazard_level = [int(v) for v in hazard_levels_string.split(',') if v]
    try:
        features = []
        boundaries = Boundary.objects.filter(
            flood_event__hazard_data__in=hazard_level).annotate(
            flood_count=Count('id')
        )
        for boundary in boundaries:
            flood_count = boundary.flood_count
            if flood_count == 0:
                continue
            parent_name = None
            if boundary.parent:
                parent_name = boundary.parent.name
            prop = {
                'name': boundary.name,
                'parent_name': parent_name,
                'flood_count': flood_count
            }
            feat = {
                'id': boundary.id,
                'type': 'Feature',
                'geometry': json.loads(boundary.geometry.geojson),
                'properties': prop
            }
            features.append(feat)
        #     rows += row
        # f.write(json.dumps(rows))

        feature_collection = {
            'type': 'FeatureCollection',
            'features': features
        }
        return JsonResponse(feature_collection)
    except Exception as e:
        LOGGER.info(e)
        return HttpResponseServerError()


def rw_histogram(
        request,
        boundary_id, start_date_timestamp=None, end_date_timestamp=None,
        hazard_levels_string=None):
    try:
        hazard_levels = [1, 2, 3, 4]
        if hazard_levels_string:
            hazard_levels = [
                int(v) for v in hazard_levels_string.split(',') if v]
        date_pattern = '%Y-%m-%d'
        start_date = datetime(2016, 1, 1)
        if start_date_timestamp:
            start_date = datetime.strptime(start_date_timestamp, date_pattern)
        end_date = datetime.utcnow()
        if end_date_timestamp:
            end_date = datetime.strptime(end_date_timestamp, date_pattern)
        events = FloodEventBoundary.objects.filter(
            boundary__id=boundary_id,
            flood__time__gte=start_date,
            flood__time__lte=end_date,
            hazard_data__in=hazard_levels
        ).order_by('flood__time')
        features = []
        last_event = None
        for e in events:
            if last_event:
                event_time_delta = (
                    e.flood.time.replace(tzinfo=None) - last_event)
                if event_time_delta < timedelta(1):
                    continue
            last_event = datetime(
                e.flood.time.year,
                e.flood.time.month,
                e.flood.time.day)
            f = {
                'event_id': e.flood.event_id,
                'time': e.flood.time.strftime(date_pattern),
                'hazard_class': e.hazard_data
            }
            features.append(f)
        return JsonResponse(features, safe=False)
    except Exception as e:
        LOGGER.info(e)
        return HttpResponseServerError()
