# coding=utf-8
from __future__ import absolute_import

import logging
import urllib2
from urlparse import urljoin
from bs4 import BeautifulSoup

from django.conf import settings
from django.core.urlresolvers import reverse

from realtime.app_settings import LOGGER_NAME, FELT_EARTHQUAKE_URL
from core.celery_app import app
from realtime.helpers.inaware import InAWARERest
from realtime.models.earthquake import Earthquake

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '3/15/16'


LOGGER = logging.getLogger(LOGGER_NAME)


@app.task(queue='inasafe-django', default_retry_delay=30 * 60, bind=True)
def push_shake_to_inaware(self, shake_id):
    """

    :param self: Required parameter if bind=True is used

    :param shake_id: The shake id of the event
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
        pdf_url = urljoin(
            settings.SITE_DOMAIN_NAME,
            pdf_url)
        inaware.post_url_product(
            hazard_id, pdf_url, 'InaSAFE Estimated Earthquake Impact - EN')
        pdf_url = reverse('realtime_report:report_pdf', kwargs={
            'shake_id': shake_id,
            'language': 'id',
            'language2': 'id',
        })
        pdf_url = urljoin(
            settings.SITE_DOMAIN_NAME,
            pdf_url)
        inaware.post_url_product(
            hazard_id, pdf_url, 'InaSAFE Perkiraan Dampak Gempa - ID')

    except ValueError as exc:
        LOGGER.debug(exc)

    except Exception as exc:
        # retry in 30 mins
        LOGGER.debug(exc)
        raise self.retry(exc=exc, countdown=30 * 60)


@app.task(queue='inasafe-django')
def retrieve_felt_earthquake_list():
    """Retrieve felt earthquake list from BMKG website

    Executed once in an hour

    :return:
    """
    # Scraped from BMKG's web
    target_url = FELT_EARTHQUAKE_URL
    try:
        response = urllib2.urlopen(target_url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        trs = soup.table.tbody.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            event_id = tds[5].a['data-target'][1:]
            try:
                shake = Earthquake.objects.get(shake_id=event_id)
                shake.felt = True
                shake.save()
            except Earthquake.DoesNotExist:
                pass
    except urllib2.URLError:
        LOGGER.debug('Failed to connect to {url}'.format(url=target_url))
