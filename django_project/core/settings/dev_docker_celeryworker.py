# coding=utf-8
import logging
import sys

# from realtime.app_settings import LOGGER_NAME
from .dev_docker import *  # noqa

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/4/15'


LOGGER = logging.getLogger(__name__)

# Enable this only for django celery debugging
sys.path.append("/pycharm-debug.egg")
