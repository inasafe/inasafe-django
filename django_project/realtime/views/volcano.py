# coding=utf-8
from rest_framework import mixins
from rest_framework.filters import DjangoFilterBackend, SearchFilter, \
    OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from realtime.models.volcano import Volcano
from realtime.serializers.volcano_serializer import VolcanoGeoJsonSerializer, \
    VolcanoSerializer

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '7/18/16'


class VolcanoList(mixins.ListModelMixin, GenericAPIView):
    queryset = Volcano.objects.all()
    serializer_class = VolcanoSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    # filter_fields = ('volcano_name', 'morphology', 'region', 'subregion')
    # filter_class = VolcanoFilter
    search_fields = ('volcano_name', )
    ordering = ('volcano_name', )
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class VolcanoFeatureList(VolcanoList):
    serializer_class = VolcanoGeoJsonSerializer
    pagination_class = None
