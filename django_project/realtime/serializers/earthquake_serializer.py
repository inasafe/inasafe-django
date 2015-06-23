# coding=utf-8
from realtime.models.earthquake import Earthquake, EarthquakeReport
from django.core.urlresolvers import reverse
from rest_framework import serializers
from rest_framework_gis.serializers import GeoModelSerializer

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '19/06/15'


class CustomSerializerMethodField(serializers.SerializerMethodField):
    """Custom Serializer Method Field.

    Includes serializing field in the method executions
    """

    def to_representation(self, value):
        method = getattr(self.parent, self.method_name)
        return method(self, value)


class EarthquakeReportSerializer(serializers.ModelSerializer):

    shake_id = serializers.SlugRelatedField(
        read_only=True,
        slug_field='shake_id',
        source='earthquake'
    )

    def get_shake_report_url(self, serializer_field, obj):
        """
        :param serializer_field:
        :type serializer_field: CustomSerializerMethodField
        :param obj:
        :type obj: EarthquakeReport
        :return:
        """
        relative_uri = reverse(
            'realtime:earthquake_report_detail',
            kwargs={
                'shake_id': obj.earthquake.shake_id,
                'language': obj.language})
        if self.context and 'request' in self.context:
            return self.context['request'].build_absolute_uri(relative_uri)
        else:
            return relative_uri

    report_url = CustomSerializerMethodField('get_shake_report_url')

    class Meta:
        model = EarthquakeReport
        fields = (
            'report_url',
            'shake_id',
            'language',
            'report_pdf',
            'report_image',
            'report_thumbnail'
        )


class EarthquakeSerializer(GeoModelSerializer):
    context = None
    reports = EarthquakeReportSerializer(
        many=True, required=False, context=context)

    class Meta:
        model = Earthquake
        fields = (
            'shake_id',
            'magnitude',
            'time',
            'depth',
            'location',
            'location_description',
            'reports'
        )
