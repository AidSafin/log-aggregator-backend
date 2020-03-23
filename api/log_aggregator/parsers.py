import abc
import re
from datetime import datetime

import pytz
from log_aggregator.models import RequestMethodsTypes


class BaseParser(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def parse(self, line) -> dict:
        pass


class ApacheLogParser(BaseParser):
    """Классс для парсинга Apache логов."""

    parts = [
        r'(?P<host>\S+)',  # host %h
        r'\S+',  # indent %l (unused)
        r'\S+',  # user %u (unused)
        r'\[(?P<time>.+)\]',  # time %t
        r'"(?P<request_method>\S+) (?P<request_path>\S+) (?P<protocol>\S+)"',  # request "%r"
        r'(?P<status>[0-9]+)',  # status %>s
        r'(?P<size>\S+)',  # size %b
        r'"(?P<referrer>.*)"',  # referrer "%{Referer}i" (unused)
        r'"(?P<agent>.*)"',  # user agent "%{User-agent}i"
        r'\S+',  # unused
    ]
    pattern = re.compile(r'\s+'.join(parts) + r'\s*\Z')
    time_format = '%d/%b/%Y:%H:%M:%S %z'

    @classmethod
    def parse(cls, line: str) -> dict:
        """Парсинг Apache логов.

        Метод принимает строку логов и возвращает словарь,
        после парсинга по `pattern`, иначе пустой словарь
        """
        matches = cls.pattern.match(line)
        if matches is None:
            return {}
        return cls.handle_data(matches.groupdict())

    @classmethod
    def handle_data(cls, data: dict):
        """Обабатывает распарсенные данные.

        Для обаботки каждого поле по отдельности необходимо создать
        метод `handle_<название поля>` который будет обрабатывать это поле
        (метод должен принимать и возвращать значение этого поля)
        """
        for attr_name, value in data.items():
            attr_handle_func = getattr(cls, 'handle_{0}'.format(attr_name), None)
            if attr_handle_func is None:
                continue

            handled_attr = attr_handle_func(value)

            if isinstance(handled_attr, str):
                handled_attr = handled_attr.strip()

            data[attr_name] = handled_attr

        return data

    @classmethod
    def handle_time(cls, value):
        return datetime.strptime(value, cls.time_format).astimezone(pytz.utc)

    @classmethod
    def handle_size(cls, value):
        if value == '-':
            return 0
        return int(value)

    @classmethod
    def handle_status(cls, value):
        return int(value)

    @classmethod
    def handle_referrer(cls, value):
        if value == '-':
            return ''
        return value

    @classmethod
    def handle_request_method(cls, value):
        return RequestMethodsTypes.get_code_from_val(value)
