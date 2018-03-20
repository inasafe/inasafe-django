# coding=utf-8
import logging
from copy import deepcopy

from django.conf import settings
from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.db.utils import IntegrityError
from django.http import HttpResponseNotFound
from django.http.response import (
    HttpResponseBadRequest,
    JsonResponse,
    HttpResponse)
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from rest_framework import status, mixins
from rest_framework.decorators import api_view
from rest_framework.filters import (
    DjangoFilterBackend,
    SearchFilter,
    OrderingFilter)
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response
from rest_framework_gis.filters import InBBoxFilter

from realtime.filters.earthquake_filter import EarthquakeFilter
from realtime.forms.earthquake import FilterForm
from realtime.helpers.rest_push_indicator import track_rest_push
from realtime.models.earthquake import Earthquake, EarthquakeReport, \
    EarthquakeMMIContour
from realtime.serializers.earthquake_serializer import (
    EarthquakeSerializer,
    EarthquakeReportSerializer,
    EarthquakeGeoJsonSerializer, EarthquakeMMIContourGeoJSONSerializer)
from realtime.tasks.earthquake import push_shake_to_inaware
from realtime.tasks.realtime.earthquake import process_shake

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '19/06/15'


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

    if request.method == 'GET':
        if 'iframe' in request.GET:
            iframe = request.GET.get('iframe')
        if 'server_side_filter' in request.GET:
            server_side_filter = request.GET.get('server_side_filter')

    context = RequestContext(request)
    return render_to_response(
        'realtime/earthquake/index.html',
        {
            'form': form,
            'iframe': iframe,
            'server_side_filter': server_side_filter,
            'select_area_text': _('Select Area'),
            'remove_area_text': _('Remove Selection'),
            'select_current_zoom_text': _('Select area within current zoom'),
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
    * since_last_days (latest EQ since the last d days)
    * since_last_hours (latest EQ since the last h hours)
    * location_description
    * in_bbox filled with BBox String in the format SWLon,SWLat,NELon,NELat
    this is used as geographic box filter
    """

    queryset = Earthquake.objects.all()
    serializer_class = EarthquakeSerializer
    # parser_classes = [JSONParser, FormParser]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,
                       InBBoxFilter)
    bbox_filter_field = 'location'
    bbox_filter_include_overlapping = True
    filter_fields = ('depth', 'magnitude', 'shake_id', 'source_type')
    filter_class = EarthquakeFilter
    search_fields = ('location_description', )
    ordering = ('shake_id', 'source_type')
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

    def get(self, request, shake_id=None, source_type=None, *args, **kwargs):
        try:
            queryset = Earthquake.objects.all()
            if shake_id or source_type:
                if shake_id:
                    queryset = queryset.filter(shake_id=shake_id)
                if source_type:
                    queryset = queryset.filter(source_type=source_type)
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
            else:
                return self.list(request, *args, **kwargs)
        except EarthquakeReport.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        retval = self.create(request, *args, **kwargs)
        track_rest_push(request)
        if not settings.DEV_MODE:
            # carefuly DO NOT push it to InaWARE when in dev_mode
            push_shake_to_inaware.delay(
                request.data.get('shake_id'),
                request.data.get('source_type'))
        return retval


class EarthquakeDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin, GenericAPIView):
    """
    Provides GET, PUT, and DELETE requests to retrieve, update and delete
    Earthquake models.
    """
    queryset = Earthquake.objects.all()
    serializer_class = EarthquakeSerializer
    lookup_field = ['shake_id', 'source_type']
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        for lookup_url in lookup_url_kwarg:
            assert lookup_url in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
            )

        filter_kwargs = {
            key: self.kwargs[key]
            for key in lookup_url_kwarg
            if self.kwargs[key]
        }
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        try:
            data = request.data
            shake_id = kwargs.get('shake_id') or data.get('shake_id')
            source_type = kwargs.get('source_type') or data.get('source_type')
            instance = Earthquake.objects.get(
                shake_id=shake_id, source_type=source_type)
            if 'shake_grid' in request.FILES and instance.shake_grid:
                instance.shake_grid.delete()
            if 'mmi_output' in request.FILES and instance.mmi_output:
                instance.mmi_output.delete()
        except Earthquake.DoesNotExist:
            pass
        retval = self.update(request, partial=True, *args, **kwargs)
        track_rest_push(request)
        return retval

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
            source_type = kwargs.get('source_type') or data.get('source_type')
            data['shake_id'] = shake_id
            data['source_type'] = source_type
            earthquake = Earthquake.objects.get(
                shake_id=shake_id,
                source_type=source_type)
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

    def get(self, request, shake_id=None, source_type=None, language=None,
            *args, **kwargs):
        try:
            if shake_id and source_type and language:
                instance = EarthquakeReport.objects.get(
                    earthquake__shake_id=shake_id,
                    earthquake__source_type=source_type,
                    language=language)
                serializer = self.get_serializer(instance)
                return Response(serializer.data)
            elif shake_id:
                return self.list(request, *args, **kwargs)
        except EarthquakeReport.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except MultipleObjectsReturned as e:
            # this should not happen.
            # But in case it is happening, returned the last object, but still
            # log the error to sentry
            LOGGER.warning(e.message)
            instance = EarthquakeReport.objects.filter(
                earthquake__shake_id=shake_id,
                earthquake__source_type=source_type,
                language=language).last()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

    def put(self, request, shake_id=None, source_type=None, language=None):
        data = request.data
        try:
            if shake_id and source_type and language:
                data['shake_id'] = shake_id
                data['source_type'] = source_type
                report = EarthquakeReport.objects.get(
                    earthquake__shake_id=shake_id,
                    earthquake__source_type=source_type,
                    language=language)
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

    def delete(self, request, shake_id, source_type, language):
        try:
            report = EarthquakeReport.objects.get(
                earthquake__shake_id=shake_id,
                earthquake__source_type=source_type,
                language=language)
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
    * since_last_days (latest EQ since the last d days)
    * since_last_hours (latest EQ since the last h hours)
    * location_description
    * felt shakes
    * in_bbox filled with BBox String in the format SWLon,SWLat,NELon,NELat
    this is used as geographic box filter
    """
    serializer_class = EarthquakeGeoJsonSerializer
    pagination_class = None

    def get(self, request, source_type='initial', *args, **kwargs):
        return super(EarthquakeFeatureList, self).get(
            request, source_type=source_type, *args, **kwargs)


class EarthquakeMMIContourList(
        mixins.ListModelMixin, GenericAPIView):
    """
    Provides GET requests to retrieve Earthquake MMI Contours
    in a GEOJSON format.

    ### Filters

    These are the available filters:

    * earthquake__shake_id
    * earthquake__source_type
    * mmi
    * in_bbox filled with BBox String in the format SWLon,SWLat,NELon,NELat
    this is used as geographic box filter
    """
    queryset = EarthquakeMMIContour.objects.all()
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    serializer_class = EarthquakeMMIContourGeoJSONSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('earthquake__shake_id', 'earthquake__source_type', 'mmi')
    search_fields = ('earthquake__shake_id', 'earthquake__source_type', 'mmi')
    ordering_fields = (
        'earthquake__shake_id', 'earthquake__source_type', 'mmi')
    ordering = ('earthquake__shake_id', 'earthquake__source_type', 'mmi')

    def get(self, request, *args, **kwargs):
        return super(EarthquakeMMIContourList, self).list(
            request, *args, **kwargs)

    def filter_queryset(self, queryset):
        shake_filter = {}
        for key, value in self.kwargs.iteritems():
            shake_filter['earthquake__' + key] = value

        queryset = queryset.filter(**shake_filter)
        return super(EarthquakeMMIContourList, self).filter_queryset(queryset)


@api_view(['GET'])
def get_corrected_shakemaps_for_shake_id(request, shake_id):
    """View to search for corrected shakemaps for a given initial id.

    :param request: A Django request object

    :param shake_id: Initial shake id of shakemaps. This can be a different ID
        from a shake_id field of a corrected shakemaps.
    """
    if request.method != 'GET':
        return HttpResponseBadRequest()

    try:
        shake = Earthquake.objects.get(
            shake_id=shake_id,
            source_type=Earthquake.INITIAL_SOURCE_TYPE)
        """:type : Earthquake"""

        # Find corrected shakemaps version
        shake_corrected = shake.corrected_shakemaps
        serializer = EarthquakeSerializer(shake_corrected)
        return Response(serializer.data)

    except Earthquake.DoesNotExist:
        return HttpResponseNotFound()


@api_view(['GET'])
def get_corrected_shakemaps_report_for_shake_id(
        request, shake_id, language='en'):
    """View to search for corrected shakemaps report for a given initial id.

    :param request: A Django request object

    :param shake_id: Initial shake id of shakemaps. This can be a different ID
        from a shake_id field of a corrected shakemaps.

    :param language: Report language to search
    """
    try:
        shake = Earthquake.objects.get(
            shake_id=shake_id,
            source_type=Earthquake.INITIAL_SOURCE_TYPE)
        """:type : Earthquake"""

        # Find corrected shakemaps version
        shake_corrected = shake.corrected_shakemaps
        """:type : Earthquake"""

        # Find shake reports
        report = shake_corrected.reports.get(language=language)
        serializer = EarthquakeReportSerializer(report)
        return Response(serializer.data)

    except Earthquake.DoesNotExist:
        return HttpResponseNotFound()


def get_grid_xml(request, shake_id, source_type):
    if request.method != 'GET':
        return HttpResponseBadRequest()

    try:
        shake = Earthquake.objects.get(
            shake_id=shake_id,
            source_type=source_type)
        if shake.shake_grid:
            response = HttpResponse(
                shake.shake_grid.read(),
                content_type='application/octet-stream')
            response['Content-Disposition'] = \
                'inline; filename="%s-grid.xml"' % shake_id
        elif shake.shake_grid_xml:
            response = HttpResponse(
                shake.shake_grid_xml,
                content_type='application/octet-stream')
            response['Content-Disposition'] = \
                'inline; filename="{0}"'.format(shake.grid_xml_filename)
        else:
            # Legacy shake grid not exists
            # TODO: Update using current workflow
            response = JsonResponse({'success': False})

        return response
    except BaseException:
        return HttpResponseBadRequest()


def get_analysis_zip(request, shake_id, source_type):
    if request.method != 'GET':
        return HttpResponseBadRequest()

    try:
        shake = Earthquake.objects.get(
            shake_id=shake_id,
            source_type=source_type)

        if shake.analysis_zip_path:
            with open(shake.analysis_zip_path) as f:
                response = HttpResponse(
                    f.read(),
                    content_type='application/octet-stream')
                response['Content-Disposition'] = \
                    'inline; filename=' \
                    '"{shake_id}-{source_type}-analysis.zip"'.format(
                        shake_id=shake_id,
                        source_type=source_type)
        else:
            # Legacy shake grid not exists
            # TODO: Update using current workflow
            response = JsonResponse({'success': False})

        return response
    except BaseException:
        return HttpResponseBadRequest()


def trigger_process_shake(request, shake_id):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    try:
        # Legacy shake grid not exists
        # TODO: Update using current workflow
        process_shake.delay(shake_id)
        return JsonResponse({'success': True})
    except BaseException:
        return HttpResponseBadRequest()
