# -*- coding: utf-8 -*-

import pytest
from asynctest import CoroutineMock

from aiohttp_baseapi.decorators import jsonify_response


class TestJsonifyResponseInit:
    def test_ok_with_status(self, mocker):
        fake_status = mocker.Mock()

        json_response = jsonify_response(status=fake_status)

        compared_func = json_response.func
        compared_status = json_response.status

        expected_func = None
        expected_status = fake_status

        assert compared_func == expected_func
        assert compared_status == expected_status

    def test_ok_wo_status(self, mocker):
        fake_function = mocker.Mock()
        mocked_http_status = mocker.patch('http.HTTPStatus')

        json_response = jsonify_response(fake_function)

        compared_func = json_response.func
        compared_status = json_response.status

        expected_func = fake_function
        expected_status = mocked_http_status.OK

        assert compared_func == expected_func
        assert compared_status == expected_status


class TestJsonifyResponseCall:
    def test_ok(self, mocker):
        fake_status = mocker.Mock()
        fake_function = mocker.Mock()

        json_response = jsonify_response(status=fake_status)
        json_response(fake_function)

        compared_func = json_response.func
        expected_func = fake_function

        assert compared_func == expected_func


class TestJsonifyResponseGet:
    @pytest.mark.asyncio
    async def test_ok(self, mocker):
        fake_base_method = CoroutineMock()
        mocked_http_status = mocker.patch('http.HTTPStatus')
        mocked_json_response = mocker.patch('aiohttp_baseapi.decorators.JSONResponse')

        class FakeClass:
            fake_method = jsonify_response(fake_base_method)

        fake_obj = FakeClass()

        compared_response = await fake_obj.fake_method()
        expected_response = mocked_json_response.return_value

        assert compared_response == expected_response

        fake_base_method.assert_called_once_with(fake_obj)
        mocked_json_response.assert_called_once_with(
            fake_base_method.return_value,
            status=mocked_http_status.OK
        )
