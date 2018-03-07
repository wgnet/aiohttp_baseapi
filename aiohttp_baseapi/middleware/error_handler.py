# -*- coding: utf-8 -*-

from aiohttp.web import HTTPNotFound, HTTPClientError

from aiohttp_baseapi.exceptions import HTTPCustomError
from aiohttp_baseapi.errors import ApiError
from aiohttp_baseapi.log import logger


INTERNAL_SERVER_ERROR_MESSAGE = 'Internal server error'


def error_handler(*, is_debug=False):
    async def error_handler_factory(app, handler):
        async def handle(request):
            try:
                return await handler(request)
            except HTTPCustomError:
                raise
            except HTTPNotFound as e:
                error = ApiError().EntityNotFound(e.body.decode())
                raise HTTPCustomError(error, HTTPNotFound.status_code)
            except HTTPClientError as e:
                # this case for 403, 405 and etc. client errors
                error = ApiError().BaseClientError(e.reason, e.body.decode())
                raise HTTPCustomError(error, e.status_code)
            except Exception as e:
                logger.exception(e)
                detail = str(e) if is_debug else INTERNAL_SERVER_ERROR_MESSAGE
                error = ApiError().InternalError(detail)
                raise HTTPCustomError(error)

        return handle
    return error_handler_factory
