# coding=utf-8
from rest_framework import serializers

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/3/15'


class CustomSerializerMethodField(serializers.SerializerMethodField):
    """Custom Serializer Method Field.

    Includes serializing field in the method executions
    """

    def to_representation(self, value):
        method = getattr(self.parent, self.method_name)
        return method(self, value)
