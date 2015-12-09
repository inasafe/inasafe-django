# coding=utf-8
from django.contrib.gis.gdal import DataSource

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/4/15'


def load_shapefile(filename):
    data_source = DataSource(filename)
    pass
