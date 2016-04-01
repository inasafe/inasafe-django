# coding=utf-8
from __future__ import absolute_import

import logging

from django.core.urlresolvers import reverse

from realtime.app_settings import LOGGER_NAME
from core.celery_app import app
from realtime.helpers.inaware import InAWARERest
from realtime.models.earthquake import Earthquake

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '3/15/16'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(queue='inasafe-django', default_retry_delay=30 * 60, bind=True)
def push_shake_to_inaware(self, shake_id):
    """

    :param shake_id:
    :type shake_id: str
    :return:
    """
    try:
        inaware = InAWARERest()
        hazard_id = inaware.get_hazard_id(shake_id)
        if not hazard_id:
            # hazard id is not there?
            # then BMKG haven't pushed it yet to InaWARE then
            raise Exception('Hazard id is none')
        pdf_url = reverse('realtime_report:report_pdf', kwargs={
            'shake_id': shake_id,
            'language': 'en',
            'language2': 'en',
        })
        inaware.post_url_product(
            hazard_id, pdf_url, 'InaSAFE Estimated Earthquake Impact - EN')
        pdf_url = reverse('realtime_report:report_pdf', kwargs={
            'shake_id': shake_id,
            'language': 'id',
            'language2': 'id',
        })
        inaware.post_url_product(
            hazard_id, pdf_url, 'InaSAFE Perkiraan Dampak Gempa - ID')

    except Exception as exc:
        # retry in 30 mins
        LOGGER.debug(exc)
        raise self.retry(exc=exc, countdown=30 * 60)
