# coding=utf-8

from django.contrib.gis.db import models
from django.contrib.gis.gdal.datasource import DataSource
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.contrib.gis.geos.point import Point

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '7/18/16'


class Volcano(models.Model):
    """Volcano model."""

    class Meta:
        """Meta class."""
        app_label = 'realtime'
        verbose_name_plural = 'Volcanoes'

    volcano_name = models.CharField(
        verbose_name='The Volcano Name',
        help_text='The name of the volcano',
        max_length=50,
        blank=False)

    location = models.PointField(
        verbose_name='Location',
        help_text='The location of the shake event in longitude and '
                  'latitude.',
        srid=4326,
        null=False,
        blank=False)

    elevation = models.IntegerField(
        verbose_name='Volcano Elevation',
        help_text='The elevation of the volcano in meters',
        default=0
    )

    region = models.CharField(
        verbose_name='The region main name',
        help_text='The region where the volcano located',
        max_length=50,
        blank=True,
    )

    subregion = models.CharField(
        verbose_name='The sub region main name',
        help_text='The sub region where the volcano located',
        max_length=50,
        blank=True,
    )

    province = models.CharField(
        verbose_name='The province name',
        help_text='The province where the volcano located',
        max_length=50,
        blank=True,
    )

    district = models.CharField(
        verbose_name='The district name',
        help_text='The district where the volcano located',
        max_length=50,
        blank=True,
    )

    morphology = models.CharField(
        verbose_name='Morphology',
        help_text='Morphology of the volcano',
        max_length=50,
        blank=True
    )

    def __unicode__(self):
        return '%s - %s - %s' % (
            self.volcano_name, self.province, self.district)


def load_volcano_data(Volcano, volcano_shapefile):
    source = DataSource(volcano_shapefile)

    layer = source[0]

    for feat in layer:
        volcano_name = feat.get('volcano na')
        elevation = feat.get('elevation')
        region = feat.get('region')
        subregion = feat.get('subregion')
        morphology = feat.get('morphology')
        province = feat.get('province')
        district = feat.get('district')

        geometry = feat.geom

        geos_geometry = GEOSGeometry(geometry.geojson)

        if not isinstance(geos_geometry, Point):
            continue

        try:
            volcano = Volcano.objects.get(
                volcano_name__iexact=volcano_name,
                province__iexact=province,
                district__iexact=district,
                morphology__iexact=morphology,)
            print 'Volcano %s already exists' % volcano.volcano_name
        except Volcano.DoesNotExist:
            volcano = Volcano.objects.create(
                volcano_name=volcano_name,
                location=geos_geometry,
                elevation=elevation,
                region=region,
                subregion=subregion,
                morphology=morphology,
                province=province,
                district=district)
            print 'Volcano %s created' % volcano.volcano_name
