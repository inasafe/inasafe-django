# coding=utf-8
from rest_framework_gis.serializers import GeoFeatureModelSerializer, \
    GeoModelSerializer

from realtime.models.volcano import Volcano

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '7/18/16'


class VolcanoSerializer(GeoModelSerializer):

    class Meta:
        model = Volcano
        fields = (
            'volcano_name',
            'elevation',
            'morphology',
            'region',
            'location',
            'subregion',
        )


class VolcanoGeoJsonSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Volcano
        geo_field = 'location'
        id = 'id'
        fields = (
            'volcano_name',
            'elevation',
            'morphology',
            'region',
            'subregion',
        )
