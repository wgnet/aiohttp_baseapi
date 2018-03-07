# -*- coding: utf-8 -*-

import pytest
from aiohttp.web import HTTPInternalServerError
from asynctest import CoroutineMock

from aiohttp_baseapi.exceptions import HTTPCustomError
from aiohttp_baseapi.middleware.error_handler import (
    error_handler,
    INTERNAL_SERVER_ERROR_MESSAGE
)


class TestErrorHandler:
    @staticmethod
    @pytest.fixture
    def fake_internal_server_error(mocker):
        class FakeHTTPInternalServerError(HTTPInternalServerError):
            __init__ = mocker.Mock(return_value=None)

        return FakeHTTPInternalServerError

    @pytest.mark.asyncio
    async def test_error_handler_ok(self, mocker):
        app = mocker.Mock()
        handler = CoroutineMock()
        request = mocker.Mock()

        factory = error_handler()
        handle_func = await factory(app, handler)
        await handle_func(request)

        handler.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_error_custom_error(self, mocker):
        app = mocker.Mock()
        fake_error = 'error'
        handler = CoroutineMock(side_effect=HTTPCustomError(fake_error))
        request = mocker.Mock()
        factory = error_handler()
        handle_func = await factory(app, handler)

        with pytest.raises(HTTPCustomError):
            await handle_func(request)

    @pytest.mark.asyncio
    async def test_unhandled_exception(self, mocker):
        fake_error_text = 'fake_error_text'
        fake_api_error = mocker.Mock(return_value=mocker.Mock(InternalError=mocker.Mock(return_value={})))
        mocked_error = mocker.patch(
            'aiohttp_baseapi.middleware.error_handler.ApiError', fake_api_error
        )

        app = mocker.Mock()
        handler = CoroutineMock(side_effect=Exception(fake_error_text))
        request = mocker.Mock()
        factory = error_handler()
        handle_func = await factory(app, handler)

        with pytest.raises(HTTPCustomError):
            await handle_func(request)

        mocked_error.return_value.InternalError.assert_called_once_with(INTERNAL_SERVER_ERROR_MESSAGE)

    @pytest.mark.asyncio
    async def test_unhandled_exception_debug_true(self, mocker):
        fake_error_text = 'fake_error_text'
        fake_api_error = mocker.Mock(return_value=mocker.Mock(InternalError=mocker.Mock(return_value={})))
        mocked_error = mocker.patch(
            'aiohttp_baseapi.middleware.error_handler.ApiError', fake_api_error
        )

        app = mocker.Mock()
        handler = CoroutineMock(side_effect=Exception(fake_error_text))
        request = mocker.Mock()
        factory = error_handler(is_debug=True)
        handle_func = await factory(app, handler)

        with pytest.raises(HTTPCustomError):
            await handle_func(request)

        mocked_error.return_value.InternalError.assert_called_once_with(fake_error_text)
