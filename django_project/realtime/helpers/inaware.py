# coding=utf-8
import os
from hammock import Hammock

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '3/15/16'


class InAWARERest(object):

    def __init__(self):
        self.host = os.environ.get('INAWARE_HOST')
        self.user = os.environ.get('INAWARE_USER')
        self.password = os.environ.get('INAWARE_PASS')
        if not self.host or not self.user or not self.password:
            raise ValueError('No INAWARE_HOST defined in environment.')
        self.inaware = Hammock(self.host, auth=(self.user, self.password))

    def get_hazard_id(self, shake_id):
        """Return InAWARE's hazard ID

        :param shake_id: BMKG's shake id
        :type shake_id: str
        :return: InAWARE's hazard ID
        :rtype: int
        """
        get_hazard_url = self.inaware.hp_srv.services.hazards(1)\
            .json.get_hazards
        query_string = "comment_text like '%%BMKG-ID%%%s%%'" % shake_id
        data = {
            'app_id': 1393,
            'where': query_string
        }
        try:
            ret = get_hazard_url.POST(data=data)
            hazards = ret.json()
            return hazards[0].get('hazard_ID')
        except BaseException:
            return None

    def post_file_product(self, hazard_id, input_file, input_filename,
                          title='Automated File Product'):
        """

        :param hazard_id: The InAWARE's hazard ID
        :type hazard_id: int

        :param input_file: The file to be used as a product
        :type input_file: str

        :param input_filename: The filename of the product
        :type input_filename: str

        :param title: The title of the product
        :type title: str

        :return: True if success
        :rtype: bool
        """
        create_product_url = self.inaware.hp_srv.services.products(2).json\
            .create_product
        data = {
            'app_id': 1393,
            'hazard_id': hazard_id,
            'file_name': input_filename,
            'title': title,
            'is_hidden': 'N',
            'security_flag': 'A',
            'product_type': 'FILE_PRODUCT',
            'parent_id': 0
        }
        files = {
            'file_upload': (input_filename, input_file)
        }
        try:
            ret = create_product_url.POST(data=data, files=files)
            retval = ret.json()
            return retval.get('description') == 'Product Created.'
        except BaseException:
            return False

    def post_url_product(self, hazard_id, url_product,
                         title='Automated URL Product'):
        """

        :param hazard_id: The InAWARE's hazard ID
        :type hazard_id: int

        :param url_product: The URL to be used as a product
        :type url_product: str

        :param title: The title of the product
        :type title: str

        :return: True if success
        :rtype: bool
        """
        create_product_url = self.inaware.hp_srv.services.products(2).json\
            .create_product
        data = {
            'app_id': 1393,
            'hazard_id': hazard_id,
            'data': url_product,
            'title': title,
            'is_hidden': 'N',
            'security_flag': 'A',
            'product_type': 'URL_PRODUCT',
            'parent_id': 0
        }
        # needed to create multipart/form-data requests
        dummy_files = {
            'file': ('', '')
        }
        try:
            ret = create_product_url.POST(data=data, files=dummy_files)
            retval = ret.json()
            return retval.get('description') == 'Product Created.'
        except BaseException:
            return False
