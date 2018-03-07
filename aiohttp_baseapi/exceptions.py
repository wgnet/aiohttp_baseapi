# -*- coding: utf-8 -*-

from http import HTTPStatus

from aiohttp.web_exceptions import HTTPError

from aiohttp_baseapi.response import json_dumps


__all__ = (
    'HTTPCustomError',
)


class HTTPCustomError(HTTPError):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, errors=None, status_code=None):
        errors = errors if errors is not None else []
        if not isinstance(errors, list):
            errors = [errors]

        self.status_code = status_code if status_code is not None else self.status_code

        super().__init__(
            content_type='application/json',
            text=self.prepare_json_error(errors)
        )

    @staticmethod
    def prepare_json_error(errors):
        return json_dumps(dict(errors=errors))
