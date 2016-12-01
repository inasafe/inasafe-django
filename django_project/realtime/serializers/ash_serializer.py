# coding=utf-8

from django.core.urlresolvers import reverse
from rest_framework import serializers
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
    GeometrySerializerMethodField)

from realtime.models.ash import Ash, AshReport
from realtime.serializers.utilities import CustomSerializerMethodField
from realtime.serializers.volcano_serializer import VolcanoSerializer

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '7/18/16'


class AshReportSerializer(serializers.ModelSerializer):

    # volcano_name = serializers.SlugRelatedField(
    #     queryset=Ash.objects.all(),
    #     read_only=False,
    #     slug_field='volcano',
    #     source='ash'
    # )

    def get_url(self, serializer_field, obj):
        """
        :param serializer_field:
        :type serializer_field: CustomSerializerMethodField
        :param obj:
        :type obj: AshReport
        :return:
        """
        dateformat = '%Y%m%d%H%M%S%z'
        relative_uri = reverse(
            'realtime:ash_report_detail',
            kwargs={
                'volcano_name': obj.ash.volcano.volcano_name,
                'event_time': obj.ash.event_time.strftime(dateformat),
                'language': obj.language})
        if self.context and 'request' in self.context:
            return self.context['request'].build_absolute_uri(relative_uri)
        else:
            return relative_uri

    # auto bind to get_url method
    url = CustomSerializerMethodField()

    def get_ash_url(self, serializer_field, obj):
        """
        :param serializer_field:
        :type serializer_field: CustomSerializerMethodField
        :param obj:
        :type obj: AshReport
        :return:
        """
        dateformat = '%Y%m%d%H%M%S%z'
        relative_uri = reverse(
            'realtime:ash_detail',
            kwargs={
                'volcano_name': obj.ash.volcano.volcano_name,
                'event_time': obj.ash.event_time.strftime(dateformat)
            })
        if self.context and 'request' in self.context:
            return self.context['request'].build_absolute_uri(relative_uri)
        else:
            return relative_uri

    # auto bind to get_shake_url method
    ash_url = CustomSerializerMethodField()

    class Meta:
        model = AshReport
        fields = (
            'url',
            'ash_url',
            'id',
            'ash',
            'language',
            'report_map',
        )


class AshSerializer(serializers.ModelSerializer):
    reports = AshReportSerializer(
        many=True, required=False, write_only=False, read_only=True)

    volcano = VolcanoSerializer(
        many=False, required=False, write_only=False, read_only=True)

    def get_url(self, serializer_field, obj):
        """
        :param serializer_field:
        :type serializer_field: CustomSerializerMethodField
        :param obj:
        :type obj: Ash
        :return:
        """
        dateformat = '%Y%m%d%H%M%S%z'
        relative_uri = reverse(
            'realtime:ash_detail',
            kwargs={
                'volcano_name': obj.volcano.volcano_name,
                'event_time': obj.event_time.strftime(dateformat)
            })
        if self.context and 'request' in self.context:
            return self.context['request'].build_absolute_uri(relative_uri)
        else:
            return relative_uri

    # auto bind to get_url method
    url = CustomSerializerMethodField()

    class Meta:
        model = Ash
        fields = (
            'url',
            'id',
            'volcano',
            'reports',
            'event_time',
            'task_status',
            'eruption_height',
        )


class AshGeoJsonSerializer(GeoFeatureModelSerializer):

    location = GeometrySerializerMethodField()
    volcano = VolcanoSerializer(many=False, read_only=True, write_only=False)

    def get_location(self, obj):
        return obj.volcano.location

    class Meta:
        model = Ash
        geo_field = 'location'
        id = 'id',
        fields = (
            'id',
            'volcano',
            'event_time',
            'alert_level',
            'task_status',
            'eruption_height',
        )
