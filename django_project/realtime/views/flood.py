# coding=utf-8
import logging
from copy import deepcopy

from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.db.utils import IntegrityError
from rest_framework import mixins, status
from rest_framework.filters import DjangoFilterBackend, SearchFilter, \
    OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response

from realtime.models.flood import Flood, FloodReport

from realtime.serializers.flood_serializer import FloodSerializer, \
    FloodReportSerializer

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '11/26/15'


LOGGER = logging.getLogger(__name__)


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
