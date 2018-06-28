# coding=utf-8
import logging

from django.contrib.gis.db import models
from django.contrib.gis.gdal.datasource import DataSource
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.contrib.gis.geos.point import Point
from django.utils.translation import ugettext_lazy as _

from realtime.app_settings import LOGGER_NAME

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '7/18/16'


LOGGER = logging.getLogger(LOGGER_NAME)


class Volcano(models.Model):
    """Volcano model."""

    class Meta:
        """Meta class."""
        app_label = 'realtime'
        verbose_name_plural = 'Volcanoes'

    volcano_id = models.CharField(
        verbose_name=_('The Volcano ID'),
        help_text=_('The ID of the volcano'),
        max_length=50,
        default='',
        blank=False)

    volcano_name = models.CharField(
        verbose_name=_('The Volcano Name'),
        help_text=_('The name of the volcano'),
        max_length=50,
        blank=False)

    location = models.PointField(
        verbose_name=_('Location'),
        help_text=_('The location of the shake event in longitude and '
                    'latitude.'),
        srid=4326,
        null=False,
        blank=False)

    elevation = models.IntegerField(
        verbose_name=_('Volcano Elevation'),
        help_text=_('The elevation of the volcano in meters'),
        default=0
    )

    region = models.CharField(
        verbose_name=_('The region main name'),
        help_text=_('The region where the volcano located'),
        max_length=50,
        blank=True,
    )

    subregion = models.CharField(
        verbose_name=_('The sub region main name'),
        help_text=_('The sub region where the volcano located'),
        max_length=50,
        blank=True,
    )

    province = models.CharField(
        verbose_name=_('The province name'),
        help_text=_('The province where the volcano located'),
        max_length=50,
        blank=True,
    )

    district = models.CharField(
        verbose_name=_('The district name'),
        help_text=_('The district where the volcano located'),
        max_length=50,
        blank=True,
    )

    morphology = models.CharField(
        verbose_name=_('Morphology'),
        help_text=_('Morphology of the volcano'),
        max_length=50,
        blank=True
    )

    timezone = models.CharField(
        verbose_name=_('TimeZone'),
        help_text=_('The TimeZone where the volcano located'),
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
        volcano_id = feat.get('volcano nu')
        volcano_name = feat.get('name')
        elevation = feat.get('elevation')
        region = feat.get('region')
        subregion = feat.get('subregion')
        morphology = feat.get('morphology')
        province = feat.get('province')
        district = feat.get('district')
        timezone = feat.get('timezone')

        geometry = feat.geom
        geometry.coord_dim = 2  # strip Z dimension

        geos_geometry = GEOSGeometry(geometry.geojson)

        if not isinstance(geos_geometry, Point):
            continue

        try:
            volcano = Volcano.objects.get(
                volcano_name__iexact=volcano_name,
                province__iexact=province,
                district__iexact=district,
                morphology__iexact=morphology,)
            LOGGER.info(
                'Volcano {0} already exists'.format(volcano.volcano_name))

            # Check for volcano id record.
            if not volcano.volcano_id:
                volcano.volcano_id = volcano_id
            # Check for volcano timezone record.
            if not volcano.timezone:
                volcano.timezone = timezone
            volcano.save()

        except Volcano.DoesNotExist:
            volcano = Volcano.objects.create(
                volcano_id=volcano_id,
                volcano_name=volcano_name,
                location=geos_geometry,
                elevation=elevation,
                region=region,
                subregion=subregion,
                morphology=morphology,
                province=province,
                district=district,
                timezone=timezone)
            LOGGER.debug(
                'Volcano {0} created'.format(volcano.volcano_name))
