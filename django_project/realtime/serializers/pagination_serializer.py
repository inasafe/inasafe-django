# coding=utf-8
__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '23/06/15'


class PageNumberPaginationSerializer(object):

    def __init__(self, model=None, serializer_class=None, data=None):
        self._count = 0
        self._next = None
        self._previous = None
        self._results = None
        self._serialized_results = None
        self.serializer_class = serializer_class
        self.model = model
        self.data = data
        self._is_valid = True
        try:
            self._count = data['count']
            self._next = data['next']
            self._previous = data['previous']
            self._results = data['results']
            self._results_serializer = []
            for d in self._results:
                serializer = serializer_class(data=d)
                if serializer.is_valid():
                    self._results_serializer.append(serializer)
                else:
                    raise AttributeError
        except AttributeError:
            self._is_valid = False

    def is_valid(self):
        return self._is_valid

    @property
    def count(self):
        return self._count

    @property
    def next_page(self):
        return self._next

    @property
    def previous_page(self):
        return self._previous

    @property
    def results(self):
        return self._results

    @property
    def results_serializer(self):
        return self._results_serializer
