# -*- coding: utf-8 -*-

from aiohttp_baseapi.exceptions import HTTPCustomError


class TestHTTPCustomErrorInit:
    def test_ok(self, mocker):
        fake_message = mocker.Mock()
        mocked_init = mocker.patch('aiohttp_baseapi.exceptions.HTTPError.__init__', return_value=None)
        mocked_prepare_json_error = mocker.patch.object(HTTPCustomError, 'prepare_json_error')

        HTTPCustomError(fake_message)

        mocked_init.assert_called_once_with(
            content_type='application/json',
            text=mocked_prepare_json_error.return_value
        )
        mocked_prepare_json_error.assert_called_once_with([fake_message])

    def test_ok_wo_message(self, mocker):
        mocked_init = mocker.patch('aiohttp_baseapi.exceptions.HTTPError.__init__', return_value=None)
        mocked_prepare_json_error = mocker.patch.object(HTTPCustomError, 'prepare_json_error')

        HTTPCustomError()

        mocked_init.assert_called_once_with(
            content_type='application/json',
            text=mocked_prepare_json_error.return_value
        )
        mocked_prepare_json_error.assert_called_once_with([])


class TestHTTPCustomErrorPrepareJsonError:
    def test_ok_dict_data(self, mocker):
        fake_data = dict(test=mocker.Mock())
        mocked_json_dumps = mocker.patch('aiohttp_baseapi.exceptions.json_dumps')

        compared_data = HTTPCustomError.prepare_json_error(fake_data)
        expected_data = mocked_json_dumps.return_value

        assert compared_data == expected_data

        mocked_json_dumps.assert_called_once_with(dict(errors=fake_data))

    def test_ok_not_dict_data(self, mocker):
        fake_data = mocker.Mock()
        mocked_json_dumps = mocker.patch('aiohttp_baseapi.exceptions.json_dumps')

        compared_data = HTTPCustomError.prepare_json_error(fake_data)
        expected_data = mocked_json_dumps.return_value

        assert compared_data == expected_data

        mocked_json_dumps.assert_called_once_with(dict(errors=fake_data))
