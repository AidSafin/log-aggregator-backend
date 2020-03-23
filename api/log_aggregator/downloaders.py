import abc
from typing import Generator

import requests


class BaseLogDownloader(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def download(self, url: str) -> Generator:
        pass


class ApacheLogDownloader(BaseLogDownloader):
    """Класс для скачивания Apache логов построчно."""

    @classmethod
    def download(cls, url: str) -> Generator:
        """Построчно отдает данные по логам.

        Сперва отдается размер всего файла в байтах,
        после отдается кортеж вида (<данные>,<размер данных в байтах>)
        """
        response = requests.get(url, stream=True)
        yield int(response.headers.get('Content-Length', 0))
        for chunk in response.iter_lines(decode_unicode=True):
            yield chunk, cls.get_chunk_len(chunk)

    @classmethod
    def get_chunk_len(cls, chunk):
        return len(chunk.encode('utf-8'))
