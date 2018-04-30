# coding=utf-8
import json
import logging

import pytz
from dateutil.parser import parse
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from rest_framework import mixins, status
from rest_framework.filters import (
    DjangoFilterBackend,
    SearchFilter,
    OrderingFilter)
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response

from realtime.app_settings import SLUG_ASH_LANDING_PAGE, \
    LANDING_PAGE_SYSTEM_CATEGORY
from realtime.forms.ash import AshUploadForm
from realtime.models.ash import Ash, AshReport
from realtime.models.coreflatpage import CoreFlatPage
from realtime.models.volcano import Volcano
from realtime.serializers.ash_serializer import (
    AshSerializer,
    AshReportSerializer,
    AshGeoJsonSerializer)

__author__ = 'lucernae'
__project_name__ = 'inasafe-django'
__filename__ = 'ash'
__date__ = '7/15/16'
__copyright__ = 'lana.pcfre@gmail.com'


LOGGER = logging.getLogger(__name__)


def index(request):
    if request.method == 'POST':
        pass

    landing_page = CoreFlatPage.objects.filter(
        slug_id=SLUG_ASH_LANDING_PAGE,
        system_category=LANDING_PAGE_SYSTEM_CATEGORY,
        language=request.LANGUAGE_CODE).first()

    context = RequestContext(request)
    return render_to_response(
        'realtime/ash/index.html',
        {
            'landing_page': landing_page,
            'LANDING_PAGE_SLUG_ID': SLUG_ASH_LANDING_PAGE,
            'LANDING_PAGE_SYSTEM_CATEGORY': LANDING_PAGE_SYSTEM_CATEGORY
        },
        context_instance=context)


@permission_required(
    perm=['realtime.add_ash'],
    login_url=reverse_lazy('realtime_admin:login'))
def upload_form(request):
    """Upload ash event."""
    context = RequestContext(request)
    if request.method == 'POST':
        form = AshUploadForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.instance

            # convert timezone from browser and add it to time information
            tz_name = instance.event_time_zone_string
            try:
                tz = pytz.timezone(tz_name)
            except BaseException:
                tz = pytz.utc

            instance.event_time = tz.localize(instance.event_time.replace(
                tzinfo=None))
            form.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('realtime:ash_index'))
    else:
        form = AshUploadForm()  # A empty, unbound form

    volcano_list = []

    for volcano in Volcano.objects.all():
        v = {
            'id': volcano.id,
            'name': str(volcano),
            'timezone': volcano.timezone
        }
        volcano_list.append(v)

    volcano_list_string = json.dumps(volcano_list)

    # Render the form
    return render_to_response(
        'realtime/ash/upload_modal.html',
        {
            'form': form,
            'volcano_list': volcano_list_string
        },
        context_instance=context)


class AshList(mixins.ListModelMixin, mixins.CreateModelMixin,
              GenericAPIView):
    """Views for Ash models."""

    queryset = Ash.objects.all()
    serializer_class = AshSerializer
    parser_classes = [JSONParser, FormParser]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    # filter_fields = ('volcano_name', 'region', 'subregion', 'morphology')
    search_fields = ('volcano__volcano_name', 'region',
                     'subregion', 'morphology')
    ordering = ('volcano__volcano_name', )
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        retval = self.create(request, *args, **kwargs)
        return retval


class AshDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                mixins.DestroyModelMixin, GenericAPIView):
    queryset = Ash.objects.all()
    serializer_class = AshSerializer
    lookup_field = 'id'
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

    def get(self, request, volcano_name=None, event_time=None):
        try:
            if volcano_name and event_time:
                instance = Ash.objects.get(
                    volcano__volcano_name__iexact=volcano_name,
                    event_time=parse(event_time))
                serializer = self.get_serializer(instance)
                return Response(serializer.data)
            else:
                return redirect(
                    'realtime:ash_list')
        except AshReport.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except MultipleObjectsReturned as e:
            # this should not happen.
            # But in case it is happening, returned the last object, but still
            # log the error to sentry
            LOGGER.warning(e.message)
            instance = AshReport.objects.filter(
                ash__volcano__volcano_name__iexact=volcano_name,
                ash__event_time=parse(event_time)).last()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

    def put(self, request, volcano_name=None, event_time=None,
            *args, **kwargs):
        try:
            if volcano_name and event_time:
                event_time = parse(event_time)
                instance = Ash.objects.get(
                    volcano__volcano_name__iexact=volcano_name,
                    event_time=event_time)
                self.kwargs.update(id=instance.id)
                if 'hazard_file' in request.FILES and instance.hazard_file:
                    instance.hazard_file.delete()
                if 'impact_files' in request.FILES and instance.impact_files:
                    instance.impact_files.delete()
                retval = self.update(request, partial=True, *args, **kwargs)
                return retval
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            LOGGER.warning(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class AshReportList(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin,
                    GenericAPIView):

    queryset = AshReport.objects.all()
    serializer_class = AshReportSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('ash__id', 'language')
    search_fields = ('ash__id', 'language')
    ordering_fields = ('ash__id', 'language')
    ordering = ('ash__id',)
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    def get(self, request, volcano_name=None, event_time=None,
            *args, **kwargs):
        try:
            if volcano_name:
                ash = Ash.objects.filter(
                    volcano__volcano_name__iexact=volcano_name)

                if event_time:
                    ash = ash.filter(
                        event_time=parse(event_time))

                instances = []
                for a in ash:
                    for r in a.reports.all():
                        instances.append(r)
                page = self.paginate_queryset(instances)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

                serializer = self.get_serializer(instances, many=True)
                return Response(serializer.data)
            else:
                return self.list(request, *args, **kwargs)
        except (AshReport.DoesNotExist, Ash.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, volcano_name=None, event_time=None, language=None):
        data = request.data
        try:
            volcano_name = volcano_name or data.get('volcano_name')
            event_time = event_time or data.get('event_time')
            language = language or data.get('language')
            ash = Ash.objects.get(
                volcano__volcano_name__iexact=volcano_name,
                event_time=parse(event_time))
            data['ash'] = ash.id
            report = ash.reports.filter(language=language)
        except Ash.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if report:
            # cannot post report if it is already exists
            serializer = AshReportSerializer(report[0])
            return Response(
                serializer.data, status=status.HTTP_400_BAD_REQUEST)

        serializer = AshReportSerializer(data=data, partial=True)

        if serializer.is_valid():
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


class AshReportDetail(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin, GenericAPIView):
    queryset = AshReport.objects.all()
    serializer_class = AshReportSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    def get(self, request, volcano_name=None, event_time=None, language=None,
            *args, **kwargs):
        try:
            if language:
                instance = AshReport.objects.get(
                    ash__volcano__volcano_name__iexact=volcano_name,
                    ash__event_time=parse(event_time),
                    language=language)
                serializer = self.get_serializer(instance)
                return Response(serializer.data)
            else:
                return redirect(
                    'realtime:ash_report_list',
                    volcano_name=volcano_name,
                    event_time=event_time)
        except AshReport.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except MultipleObjectsReturned as e:
            # this should not happen.
            # But in case it is happening, returned the last object, but still
            # log the error to sentry
            LOGGER.warning(e.message)
            instance = AshReport.objects.filter(
                ash__volcano__volcano_name__iexact=volcano_name,
                ash__event_time=parse(event_time),
                language=language).last()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

    def put(self, request, volcano_name=None, event_time=None, language=None):
        data = request.data
        try:
            if volcano_name and event_time and language:
                report = AshReport.objects.get(
                    ash__volcano__volcano_name__iexact=volcano_name,
                    ash__event_time=parse(event_time),
                    language=language)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except AshReport.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # delete previous files
        report.report_map.delete()
        serializer = AshReportSerializer(report, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, volcano_name, event_time, language):
        try:
            report = AshReport.objects.get(
                ash__volcano__volcano_name__iexact=volcano_name,
                ash__event_time=parse(event_time),
                language=language)
        except AshReport.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def ash_report_map(request, volcano_name, event_time, language='en'):
    """View to serve pdf report."""
    try:
        instance = AshReport.objects.get(
            ash__volcano__volcano_name__iexact=volcano_name,
            ash__event_time=parse(event_time),
            language=language)
        response = HttpResponse(
            instance.report_map.read(),
            content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="{0}";'.format(
            instance.report_map_filename)
        return response
    except AshReport.DoesNotExist:
        raise Http404()


class AshFeatureList(AshList):
    serializer_class = AshGeoJsonSerializer
    pagination_class = None
