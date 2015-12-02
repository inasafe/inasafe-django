# coding=utf-8
import logging
import threading

from django.core.files.temp import NamedTemporaryFile
from django.db import connections

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '11/30/15'


LOGGER = logging.getLogger(__name__)


def test_concurrently(times):
    """
    Add this decorator to small pieces of code that you want to test
    concurrently to make sure they don't raise exceptions when run at the
    same time.  E.g., some Django views that do a SELECT and then a
    subsequent INSERT might fail when the INSERT assumes that the data
    has not changed since the SELECT.

    # NOQA Flake8 ignore long url
    Soure : https://www.caktusgroup.com/blog/2009/05/26/testing-django-views-for-concurrency-issues/

    :param times: Number of times the method is executed
    :type times: int
    """
    def test_concurrently_decorator(test_func):
        def wrapper(*args, **kwargs):
            exceptions = []

            def call_test_func():
                try:
                    test_func(*args, **kwargs)
                except Exception, e:
                    exceptions.append(e)
                    raise
            threads = []
            for i in range(times):
                threads.append(threading.Thread(target=call_test_func))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            if exceptions:
                raise Exception(
                    'test_concurrently intercepted %s exceptions: %s' % (
                        len(exceptions), exceptions))
        return wrapper
    return test_concurrently_decorator


def close_db_connections(func, *args, **kwargs):
    """
    Decorator to close db connections during threaded execution

    Note this is necessary to work around:
    https://code.djangoproject.com/ticket/22420
    """
    def _inner(*args, **kwargs):
        func(*args, **kwargs)
        LOGGER.warning('Closing db connections.')
        for conn in connections.all():
            LOGGER.warning('Closing connection %s' % conn)
            conn.close()
    return _inner


class download_url(object):
    """Class to download file url

    Used *with* statement
    """
    def __init__(self, client, url):
        """Download a given url to temp directory.

        :param client: The APIRequestFactory client
        :type client: APIRequestFactory

        :param url: The url
        :type url: str
        """
        self.client = client
        response = self.client.get(url, stream=True)
        file = NamedTemporaryFile()
        for chunk in response.streaming_content:
            if chunk:
                file.write(chunk)
        self._file = file

    def __enter__(self):
        """Download a given url to temp directory.

        :return: The file
        :rtype: NamedTemporaryFile
        """
        return self._file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()
