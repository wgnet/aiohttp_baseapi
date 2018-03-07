# -*- coding: utf-8 -*-

import asyncio
import http

from aiohttp_baseapi.response import JSONResponse


__all__ = (
    'classproperty',
    'cachedproperty',
    'jsonify_response',
)


class classproperty(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, instance_cls=None):
        return self.func(instance_cls)


class cachedproperty(object):
    def __init__(self, func):
        assert not asyncio.iscoroutine(func), "You can not use cachedproperty decorator for async functions"

        self.func = func

    def __get__(self, instance, instance_cls=None):
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result


class JSONResponseDecorator:
    """
    Examples:
        @json_response
        async def any_response_handler(request):
          pass


        @json_response(status=201)
        async def any_response_handler(request):
          pass

    """
    def __init__(self, *args, **kwargs):
        self.func = args[0] if (len(args) == 1 and callable(args[0])) else None
        self.status = kwargs.get('status', http.HTTPStatus.OK)

    def __call__(self, func):
        self.func = func

        return self

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        async def json_response_wrapper(*args, **kwargs):
            data = await self.func(instance, *args, **kwargs)

            return JSONResponse(data, status=self.status)

        return json_response_wrapper


jsonify_response = JSONResponseDecorator
