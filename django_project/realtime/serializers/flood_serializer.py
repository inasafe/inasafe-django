# coding=utf-8

from django.core.urlresolvers import reverse
from rest_framework import serializers
from realtime.models.flood import Flood, FloodReport
from realtime.serializers.utilities import CustomSerializerMethodField

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '11/26/15'


class FloodReportSerializer(serializers.ModelSerializer):

    event_id = serializers.SlugRelatedField(
        queryset=Flood.objects.all(),
        read_only=False,
        slug_field='event_id',
        source='flood'
    )

    def get_url(self, serializer_field, obj):
        """
        :param serializer_field:
        :type serializer_field: CustomSerializerMethodField
        :param obj:
        :type obj: FloodReport
        :return:
        """
        relative_uri = reverse(
            'realtime:flood_report_detail',
            kwargs={
                'event_id': obj.flood.event_id,
                'language': obj.language})
        if self.context and 'request' in self.context:
            return self.context['request'].build_absolute_uri(relative_uri)
        else:
            return relative_uri

    # auto bind to get_url method
    url = CustomSerializerMethodField()

    def get_flood_url(self, serializer_field, obj):
        """
        :param serializer_field:
        :type serializer_field: CustomSerializerMethodField
        :param obj:
        :type obj: FloodReport
        :return:
        """
        relative_uri = reverse(
            'realtime:flood_detail',
            kwargs={'event_id': obj.flood.event_id})
        if self.context and 'request' in self.context:
            return self.context['request'].build_absolute_uri(relative_uri)
        else:
            return relative_uri

    # auto bind to get_shake_url method
    flood_url = CustomSerializerMethodField()

    class Meta:
        model = FloodReport
        fields = (
            'url',
            'flood_url',
            'event_id',
            'language',
            'impact_report',
            'impact_map',
        )


class FloodSerializer(serializers.ModelSerializer):
    reports = FloodReportSerializer(
        many=True, required=False, write_only=False,
        read_only=True
    )

    def get_url(self, serializer_field, obj):
        """
        :param serializer_field:
        :type serializer_field: CustomSerializerMethodField
        :param obj:
        :type obj: Flood
        :return:
        """
        relative_uri = reverse(
            'realtime:flood_detail',
            kwargs={
                'event_id': obj.event_id})
        if self.context and 'request' in self.context:
            return self.context['request'].build_absolute_uri(relative_uri)
        else:
            return relative_uri

    # auto bind to get_url method
    url = CustomSerializerMethodField()

    class Meta:
        model = Flood
        fields = (
            'url',
            'event_id',
            'time',
            'interval',
            'source',
            'region',
            'hazard_layer',
            'impact_layer',
            'reports'
        )


# class FloodHazardGeoJsonSerializer(GeoFeatureModelSerializer):
#
#     class Meta:
#         model = FloodEventBoundary
#         geo_field = ""
