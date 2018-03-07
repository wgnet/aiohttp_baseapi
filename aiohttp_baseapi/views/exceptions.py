# -*- coding: utf-8 -*-

from http import HTTPStatus

from aiohttp_baseapi.exceptions import HTTPCustomError


class ViewError(HTTPCustomError):
    status_code = HTTPStatus.BAD_REQUEST


class ViewValidationError(ViewError):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY


class ViewNotFoundError(ViewError):
    status_code = HTTPStatus.NOT_FOUND
