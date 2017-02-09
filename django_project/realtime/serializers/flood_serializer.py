# coding=utf-8
import pytz
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

    def get_time_description(self, serializer_field, obj):
        """
        :param serializer_field:
        :type serializer_field: CustomSerializerMethodField

        :param obj:
        :type obj: Flood

        :return:
        """
        utc_time = obj.time.replace(tzinfo=pytz.utc)
        jakarta_time = utc_time.astimezone(tz=pytz.timezone('Asia/Jakarta'))
        description_format = (
            '{interval} hour report for %d %B %Y at %H:%M:%S').format(
            interval=obj.interval)
        return jakarta_time.strftime(description_format)

    # auto bind to get_time_description method
    time_description = CustomSerializerMethodField()

    def get_event_id_formatted(self, serializer_field, obj):
        """
        :param serializer_field:
        :type serializer_field: CustomSerializerMethodField

        :param obj:
        :type obj: Flood

        :return:
        """
        utc_time = obj.time.replace(tzinfo=pytz.utc)
        jakarta_time = utc_time.astimezone(tz=pytz.timezone('Asia/Jakarta'))
        event_id_format = '%Y%m%d%H%M%S'
        return jakarta_time.strftime(event_id_format)

    # auto bind to get_event_id_formatted method
    event_id_formatted = CustomSerializerMethodField()

    class Meta:
        model = Flood
        fields = (
            'url',
            'event_id',
            'data_source',
            'event_id_formatted',
            'time',
            'time_description',
            'total_affected',
            'boundary_flooded',
            'interval',
            'source',
            'region',
            'hazard_layer',
            'impact_layer',
            'reports'
        )
