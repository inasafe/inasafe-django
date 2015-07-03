# coding=utf-8
from django.conf import settings

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '03/07/15'


# LOGO/BRAND
default_brand_logo = 'img/logo.png'
BRAND_LOGO = getattr(settings, 'FRONTEND_BRAND_LOGO', default_brand_logo)
