# coding=utf-8
from realtime.models.earthquake import Earthquake, EarthquakeReport
from rest_framework import serializers
from rest_framework_gis.serializers import GeoModelSerializer

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '19/06/15'


class EarthquakeReportSerializer(serializers.ModelSerializer):

    shake_id = serializers.SlugRelatedField(
        read_only=True,
        slug_field='shake_id',
        source='earthquake'
    )

    class Meta:
        model = EarthquakeReport
        fields = (
            'shake_id',
            'language',
            'report_pdf',
            'report_image',
            'report_thumbnail'
        )


class EarthquakeSerializer(GeoModelSerializer):
    reports = EarthquakeReportSerializer(many=True, required=False)

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
