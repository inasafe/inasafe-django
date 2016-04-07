# coding=utf-8
import unittest

import os

from realtime.helpers.inaware import InAWARERest

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '3/15/16'


class InAWARETest(unittest.TestCase):

    def setUp(self):
        self.inaware = InAWARERest()
        self.pdf_file = os.path.join(
            os.path.dirname(__file__),
            'data/20151209215811-en.pdf')

    def test_get_hazard_id(self):
        shake_id = '20151209215811'
        hazard_id = self.inaware.get_hazard_id(shake_id)
        expected_value = 3297
        self.assertEqual(hazard_id, expected_value)

    def test_post_url_product(self):
        shake_id = '20151209215811'
        hazard_id = self.inaware.get_hazard_id(shake_id)
        shake_url = 'http://realtime.inasafe.org/media/reports/earthquake/' \
                    'pdf/20151209215811-en.pdf'
        ret = self.inaware.post_url_product(
            hazard_id, shake_url, title='InaSAFE Analysis Result PDF')
        self.assertEqual(ret, True)

    def test_post_file_product(self):
        shake_id = '20151209215811'
        hazard_id = self.inaware.get_hazard_id(shake_id)
        pdf_path = self.pdf_file
        ret = self.inaware.post_file_product(
            hazard_id,
            open(pdf_path),
            os.path.basename(pdf_path),
            'InaSAFE Analysis Result PDF file'
        )
        self.assertEqual(ret, True)
