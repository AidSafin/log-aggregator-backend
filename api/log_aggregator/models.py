from django.db import models


class RequestMethodsTypes:
    GET = 0
    POST = 1
    DELETE = 2
    OPTIONS = 3
    PATCH = 4
    PUT = 5
    HEAD = 6
    NONE = 7

    data = {
        GET: 'GET',
        POST: 'POST',
        DELETE: 'DELETE',
        OPTIONS: 'OPTIONS',
        PATCH: 'PATCH',
        PUT: 'PUT',
        HEAD: 'HEAD',
        NONE: 'Undefined',
    }

    _inv_data = {name: code for code, name in data.items()}

    choices = tuple(data.items())

    @classmethod
    def get_code_from_val(cls, value: str):
        return cls._inv_data.get(value.upper(), cls.NONE)


class ApacheLog(models.Model):
    host = models.GenericIPAddressField()
    time = models.DateTimeField()
    request_method = models.PositiveSmallIntegerField(choices=RequestMethodsTypes.choices)
    request_path = models.TextField()
    protocol = models.CharField(max_length=50)
    status = models.PositiveIntegerField()
    size = models.PositiveIntegerField()
    agent = models.TextField()
    referrer = models.TextField()

    class Meta:
        verbose_name = 'Apache лог'
        verbose_name_plural = 'Apache логи'
