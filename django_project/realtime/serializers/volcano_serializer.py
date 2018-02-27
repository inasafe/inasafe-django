# coding=utf-8
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from realtime.models.volcano import Volcano

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '7/18/16'


class VolcanoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Volcano
        fields = (
            'volcano_name',
            'elevation',
            'morphology',
            'region',
            'location',
            'subregion',
            'province',
            'district',
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
            'province',
            'district',
        )
