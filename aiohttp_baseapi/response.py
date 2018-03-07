# -*- coding: utf-8 -*-

import http
from datetime import datetime

import simplejson as json
from aiohttp.web import json_response

__all__ = (
    'json_dumps',
    'JSONResponse'
)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            # Hot fix to add +0000 to all dates
            return '{}+0000'.format(obj.isoformat(timespec='seconds'))
        return super().default(obj)


def json_dumps(data):
    return json.dumps(data, cls=DateTimeEncoder)


class JSONResponse:
    empty_data = dict()

    def __new__(cls, data=None, status=http.HTTPStatus.OK):
        return json_response(data or cls.empty_data, status=status, dumps=json_dumps)
