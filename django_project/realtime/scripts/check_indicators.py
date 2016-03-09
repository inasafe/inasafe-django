# coding=utf-8
"""This script will be ran nightly by cronjob.

It is used to report critical indicator
"""
import logging
from realtime.app_settings import LOGGER_NAME
from realtime.helpers.realtime_broker_indicator import RealtimeBrokerIndicator
from realtime.helpers.shake_event_indicator import ShakeEventIndicator
from realtime.helpers.shakemap_push_indicator import ShakemapPushIndicator

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '04/09/15'


LOGGER = logging.getLogger(LOGGER_NAME)


def check_indicator_status():
    """Check all indicator and send email if it reaches critical status."""
    indicators = [
        ShakemapPushIndicator(),
        ShakeEventIndicator(),
        RealtimeBrokerIndicator(),
    ]

    for ind in indicators:
        if ind.is_critical():
            # this logging will send a log error to sentry and then emails.
            LOGGER.error(
                'Indicator reaches Critical Level : %s with value : %s',
                ind.label,
                ind.value_humanize)

if __name__ == '__main__':
    check_indicator_status()
