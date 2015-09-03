# coding=utf-8
"""This script will be ran nightly by cronjob.

It is used to report critical indicator
"""
import logging
from realtime.app_settings import LOGGER_NAME
from realtime.helpers.rest_push_indicator import RESTPushIndicator
from realtime.helpers.shake_event_indicator import ShakeEventIndicator
from realtime.helpers.shakemap_push_indicator import ShakemapPushIndicator

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '04/09/15'


LOGGER = logging.getLogger(LOGGER_NAME)

if __name__ == '__main__':
    indicators = [
        ShakemapPushIndicator(),
        ShakeEventIndicator(),
        RESTPushIndicator()
    ]

    for ind in indicators:
        if ind.is_critical():
            # this logging will send a log error to sentry and then emails.
            LOGGER.error(
                'Indicator reaches Critical Level : %s with value : %s',
                ind.label,
                ind.value_humanize
            )
