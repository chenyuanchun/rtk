import logging
import os
import requests
import warnings

from abc import ABC, abstractmethod
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError

_logger = logging.getLogger(__name__)


class RestClient:
    """Client to access REST API"""
    _BASE_URLS = {
    }

    ATTR_SUMMARY = 'summary'
    ATTR_TOTAL = 'totalHits'
    ATTR_RESULTS = 'results'

    MODEL_GEM = ''
    MODEL_QML = ''
    MODEL_KEYS = ''

    STORE_LIVE = ''
    STORE_HISTORY = ''

    def __init__(self, **config):
        """
        Init with key/value
        :param config: env, path, url, username, password
        """
        # default configurations
        self.configuration = {
            'env': None,
            'path': '/path/to'
        }

        username = os.environ.get('username')
        if username:
            self.configuration['username'] = username
        password = os.environ.get('password')
        if password:
            self.configuration['password'] = password
        if config:
            self.configuration.update(config)
        assert 'username' in self.configuration and 'password' in self.configuration, \
            "Authentication must be provide by 'username' and 'password'"

        if 'url' not in self.configuration:
            # assert 'path' in self.configuration, "GoldenEye path not provided"
            self.configuration['url'] = RestClient._BASE_URLS[self.configuration['env']] + self.configuration['path']

        warnings.filterwarnings('ignore', message='Unverified HTTPS request')

    def reset_path(self, path, env=None):
        assert path, "path must be supplied"
        self.configuration['path'] = path
        env = env if env else self.configuration['env']
        self.configuration['url'] = RestClient._BASE_URLS[env] + path

    def query_by_params(self, **params):
        url = self.configuration['url']
        _logger.info(f'Querying {url}, params: {params}')
        username = self.configuration['username']
        password = self.configuration['password']

        response = requests.get(url, params=params, verify=False, auth=HTTPBasicAuth(username, password))
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPError(f'GoldenEye request failed, status code: {response.status_code}, error: {response.reason}')


class FilterBuilder(ABC):
    @abstractmethod
    def build(self) -> str:
        """build the GE filter string used as 'filter' parameter"""


class EQ(FilterBuilder):
    def build(self):
        criteria = []
        for key, value in self._data.items():
            value = f'"{value}"' if isinstance(value, str) else value
            criteria.append(f'"{key}": {value}')
        return f'{{{",".join(criteria)}}}'

    def __init__(self, **kwargs):
        self._data = kwargs


class Cursor(FilterBuilder):
    def build(self) -> str:
        """
        generate filter string from 'nextCursor' attribute
        :return:

        >>> Cursor({'eventId': {'$lt': 161857839495613}}).build()
        '{"eventId":{"$lt": 161857839495613}}'
        """
        assert self._data, 'nextCursor must be supplied'
        key, value = next(iter(self._data.items()))
        op, id_value = next(iter(value.items()))
        return f'{{"{key}":{{"{op}": {id_value}}}}}'

    def __init__(self, next_cursor: dict):
        self._data = next_cursor


class ListOperator(FilterBuilder):
    def __init__(self, oper, **kwargs):
        assert len(kwargs) == 1, "only accepts <keyword>=<list>"
        self._key, lst = next(iter(kwargs.items()))
        self._list = list(map(lambda x: f'"{x}"', lst))
        self._operator = oper

    def build(self) -> str:
        """
        generates filter string for $in operator of GE API
        :return: filter string

        >>> IN(leShortCode=["","A","B","C"]).build()
        '{"leShortCode":{"$in":["","A","B","C"]}}'
        >>> IN(deskGuid=["001","002","003"]).build()
        '{"deskGuid":{"$in":["001","002","003"]}}'
        >>> NIN(leShortCode=["","A","B","C"]).build()
        '{"leShortCode":{"$nin":["","A","B","C"]}}'
        """
        assert self._operator, "Operator must be supplied"
        return f'{{"{self._key}":{{"{self._operator}":[{",".join(self._list)}]}}}}'


class IN(ListOperator):
    def __init__(self, **kwargs):
        super().__init__('$in', **kwargs)


class NIN(ListOperator):
    def __init__(self, **kwargs):
        super().__init__('$nin', **kwargs)


# TBD: regex
class TimeRange(FilterBuilder):
    def __init__(self, start=None, end=None):
        assert start or end, "start and/or end must be supplied"
        self.start = start
        self.end = end

    def build(self) -> str:
        """
        build filter string for time range
        :return: time range filter string

        >>> TimeRange(start='2021-04-26T05:45:00Z', end='2021-04-26T05:46:00Z').build()
        '{"ingestionTs":{"$gte":{"$date":"2021-04-26T05:45:00Z"},"$lte":{"$date":"2021-04-26T05:46:00Z"}}}'
        >>> TimeRange(start='2021-04-26T05:45:00Z').build()
        '{"ingestionTs":{"$gte":{"$date":"2021-04-26T05:45:00Z"}}}'
        >>> TimeRange(end='2021-04-26T05:46:00Z').build()
        '{"ingestionTs":{"$lte":{"$date":"2021-04-26T05:46:00Z"}}}'
        """
        _gte = f'"$gte":{{"$date":"{self.start}"}}' if self.start else None
        _lte = f'"$lte":{{"$date":"{self.end}"}}' if self.end else None
        ts = ','.join((_gte, _lte)) if _gte and _lte else None
        if not ts:
            ts = _gte if _gte else _lte
        return f'{{"ingestionTs":{{{ts}}}}}'


class Logical(FilterBuilder):
    def build(self):
        return f'{{"{self.operator}":[{",".join(self.operands)}]}}'

    def __init__(self, _operator, *args):
        self.operator = _operator
        self.operands = []
        for arg in args:
            assert isinstance(arg, FilterBuilder), 'Operand of And operator must be a FilterBuilder'
            self.operands.append(arg.build())


class AND(Logical):
    def __init__(self, *args):
        super().__init__('$and', *args)


class OR(Logical):
    def __init__(self, *args):
        super().__init__('$or', *args)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
