# coding=utf-8
from realtime.models.earthquake import Earthquake
from rest_framework_gis import serializers

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '19/06/15'


class EarthquakeSerializer(serializers.GeoModelSerializer):

    class Meta:
        model = Earthquake
        fields = (
            'shake_id',
            'magnitude',
            'time',
            'depth',
            'location',
            'location_description',
            'report_pdf',
            'report_image',
            'report_thumbnail'
        )
