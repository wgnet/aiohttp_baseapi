# -*- coding: utf-8 -*-

import http
from datetime import datetime, date

import pytest

from aiohttp_baseapi.response import DateTimeEncoder, json_dumps, JSONResponse


class TestDateTimeEncoder:
    def test_ok(self, mocker):
        fake_obj = mocker.Mock(spec=datetime)

        datetime_encoder = DateTimeEncoder()

        compared_obj = datetime_encoder.default(fake_obj)
        expected_obj = '{}+0000'.format(fake_obj.isoformat.return_value)

        assert compared_obj == expected_obj

    def test_ok_wo_datetime_obj(self, mocker):
        fake_obj = mocker.Mock()
        mocked_default = mocker.patch('aiohttp_baseapi.response.json.JSONEncoder.default')

        datetime_encoder = DateTimeEncoder()

        compared_obj = datetime_encoder.default(fake_obj)
        expected_obj = mocked_default.return_value

        assert compared_obj == expected_obj

        mocked_default.assert_called_once_with(fake_obj)

    def test_ok_date_obj(self, mocker):
        fake_obj = mocker.Mock(spec=date)
        mocked_default = mocker.patch('aiohttp_baseapi.response.json.JSONEncoder.default')

        datetime_encoder = DateTimeEncoder()

        compared_obj = datetime_encoder.default(fake_obj)
        expected_obj = mocked_default.return_value

        assert compared_obj == expected_obj

        mocked_default.assert_called_once_with(fake_obj)


class TestJsonDumps:
    def test_ok(self, mocker):
        fake_data = mocker.Mock()
        mocked_datime_encoder = mocker.patch('aiohttp_baseapi.response.DateTimeEncoder')
        mocked_dumps = mocker.patch('aiohttp_baseapi.response.json.dumps')

        compared_data = json_dumps(fake_data)
        expected_data = mocked_dumps.return_value

        assert compared_data == expected_data

        mocked_dumps.assert_called_once_with(
            fake_data,
            cls=mocked_datime_encoder
        )


class TestJSONResponse:
    @staticmethod
    @pytest.fixture
    def mocked_json_response(mocker):
        return mocker.patch('aiohttp_baseapi.response.json_response')

    @staticmethod
    @pytest.fixture
    def mocked_json_dumps(mocker):
        return mocker.patch('aiohttp_baseapi.response.json_dumps')

    def test_ok(self, mocked_json_response, mocked_json_dumps, mocker):
        fake_data = mocker.Mock()
        fake_status = mocker.Mock()

        compared_response = JSONResponse(fake_data, status=fake_status)
        expected_response = mocked_json_response.return_value

        assert compared_response == expected_response

        mocked_json_response.assert_called_once_with(
            fake_data,
            status=fake_status,
            dumps=mocked_json_dumps
        )

    def test_wo_data_wo_status(self, mocked_json_response, mocked_json_dumps, mocker):
        mocked_empty_data = mocker.patch('aiohttp_baseapi.response.JSONResponse.empty_data')

        compared_response = JSONResponse()
        expected_response = mocked_json_response.return_value

        assert compared_response == expected_response

        mocked_json_response.assert_called_once_with(
            mocked_empty_data,
            status=http.HTTPStatus.OK,
            dumps=mocked_json_dumps
        )
