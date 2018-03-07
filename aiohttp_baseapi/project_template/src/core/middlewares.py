# -*- coding: utf-8 -*-

from aiohttp.web_middlewares import normalize_path_middleware
from aiohttp_baseapi.middleware.error_handler import error_handler
from aiohttp_baseapi.middleware.params_handler import params_handler

from conf import settings

__all__ = (
    'middlewares',
)

middlewares = list()

middlewares.append(normalize_path_middleware())
middlewares.append(params_handler)
middlewares.append(error_handler(is_debug=settings.DEBUG))
