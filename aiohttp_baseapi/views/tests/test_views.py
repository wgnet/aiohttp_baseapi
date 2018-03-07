# -*- coding: utf-8 -*-

import pytest
from pytest_mock import MockFixture

from aiohttp_baseapi.views.base import BaseDataProviderView
from aiohttp_baseapi.views.exceptions import ViewValidationError


@pytest.fixture
def fake_base_view_cls():
    class FakeBaseView(BaseDataProviderView):
        async def get(self):
            pass

    return FakeBaseView


@pytest.fixture
def fake_base_view_obj(mocker: MockFixture, fake_base_view_cls):
    mocker.patch('aiohttp_baseapi.views.base.BaseDataProviderView.__init__', return_value=None)
    mocker.patch.object(fake_base_view_cls, 'Meta')

    return fake_base_view_cls()


class TestBaseViewInit:
    def test_ok(self, mocker: MockFixture):
        fake_instance = mocker.Mock(__class__=BaseDataProviderView)
        mocked_super_init = mocker.patch('aiohttp_baseapi.views.base.web.View.__init__')
        mocked_request = mocker.Mock()

        BaseDataProviderView.__init__(fake_instance, mocked_request)

        mocked_super_init.assert_called_once()
        fake_instance.validate_filters.assert_called_once()
        fake_instance.validate_page.assert_called_once()
        fake_instance.validate_includes.assert_called_once()
        fake_instance.validate_sort.assert_called_once()

    def test_error(self, mocker, fake_base_view_cls):
        mocked_super_init = mocker.patch('aiohttp_baseapi.views.base.web.View.__init__')
        mocked_request = mocker.Mock()
        with pytest.raises(AssertionError):
            fake_base_view_cls(mocked_request)

        mocked_super_init.assert_called_once()


class TestBaseViewAvailableIncludes:
    def test_ok(self, mocker: MockFixture, fake_base_view_obj: BaseDataProviderView):
        fake_available_includes = mocker.Mock()
        mocker.patch.object(fake_base_view_obj.Meta, 'available_includes', fake_available_includes)

        compared_result = fake_base_view_obj.available_includes
        expected_result = fake_available_includes

        assert compared_result == expected_result


class TestBaseViewValidatePage:
    def test_ok(self, mocker: MockFixture, fake_base_view_cls):
        fake_updated_value = 100

        fake_object = mocker.Mock(**{
            '_page.get.return_value': fake_updated_value,
            'MAX_LIMIT': 1000,
            'ITEMS_ON_PAGE': 100
        })
        mocker.patch.object(fake_object, '_page.update')
        fake_base_view_cls.validate_page(fake_object)

        fake_object._page.get.assert_has_calls([
            mocker.call('limit', fake_object.DEFAULT_LIMIT),
            mocker.call('offset', fake_object.DEFAULT_OFFSET),
        ])
        fake_object._page.update.assert_called_once_with({'limit': fake_updated_value, 'offset': fake_updated_value})

    def test_error_max_limit(self, mocker: MockFixture, fake_base_view_cls):
        fake_object = mocker.Mock(**{
            '_page.get.return_value': 100,
            'MAX_LIMIT': 10
        })
        with pytest.raises(ViewValidationError):
            fake_base_view_cls.validate_page(fake_object)

    def test_error_not_integer(self, mocker: MockFixture, fake_base_view_cls):
        fake_object = mocker.Mock(**{
            '_page.get.return_value': 'foo',
        })
        with pytest.raises(ViewValidationError):
            fake_base_view_cls.validate_page(fake_object)


class TestBaseViewValidateFilters:
    def test_ok(self, mocker: MockFixture, fake_base_view_cls):
        fake_filters = dict(test=mocker.Mock())
        fake_available_filters = ['test']
        mocked_validation_error = mocker.patch('aiohttp_baseapi.views.exceptions.ViewValidationError')
        fake_object = mocker.Mock(
            _filters=fake_filters,
            available_filters=fake_available_filters,
        )

        fake_base_view_cls.validate_filters(fake_object)

        mocked_validation_error.assert_not_called()

    def test_error(self, mocker: MockFixture, fake_base_view_cls):
        fake_filters = dict(unknown=mocker.Mock())
        fake_available_filters = ['test']
        fake_object = mocker.Mock(
            _filters=fake_filters,
            available_filters=fake_available_filters,
        )

        with pytest.raises(ViewValidationError):
            fake_base_view_cls.validate_filters(fake_object)

    def test_error_comparison(self, mocker: MockFixture, fake_base_view_cls):
        fake_filters = dict(test__gte=[mocker.Mock(), mocker.Mock()])
        fake_available_filters = ['test']
        mocked_get_comparison_operator = mocker.Mock()

        fake_object = mocker.Mock(
            _filters=fake_filters,
            available_filters=fake_available_filters,
            get_comparison_operator=mocked_get_comparison_operator)

        with pytest.raises(ViewValidationError):
            fake_base_view_cls.validate_filters(fake_object)


class TestBaseViewValidateIncludes:
    def test_ok(self, mocker: MockFixture, fake_base_view_cls):
        fake_includes = dict(test=mocker.Mock())
        fake_available_includes = ['test']
        mocked_validation_error = mocker.patch('aiohttp_baseapi.views.exceptions.ViewValidationError')
        fake_object = mocker.Mock(
            _include=fake_includes,
            available_includes=fake_available_includes
        )

        fake_base_view_cls.validate_includes(fake_object)

        fake_object._validate_include_params.assert_called_once()
        mocked_validation_error.assert_not_called()

    def test_error(self, mocker: MockFixture, fake_base_view_cls):
        fake_includes = dict(unknown=mocker.Mock())
        fake_available_includes = ['test']

        fake_object = mocker.Mock(_include=fake_includes, available_includes=fake_available_includes)

        with pytest.raises(ViewValidationError):
            fake_base_view_cls.validate_includes(fake_object)


class TestBaseViewDataProvider:
    def test_ok(self, mocker: MockFixture, fake_base_view_obj: BaseDataProviderView):
        fake_data_provider_params = dict(test=mocker.Mock())
        mocked_get_data_provider_params = mocker.patch.object(
            fake_base_view_obj,
            'get_data_provider_params',
            return_value=fake_data_provider_params
        )

        compared_data = fake_base_view_obj.data_provider
        expected_data = fake_base_view_obj.Meta.data_provider_class.return_value

        assert compared_data == expected_data

        mocked_get_data_provider_params.assert_called_once()
        fake_base_view_obj.Meta.data_provider_class.assert_called_once_with(**fake_data_provider_params)


class TestBaseViewGetFilters:
    def test_ok(self, mocker: MockFixture, fake_base_view_obj: BaseDataProviderView):
        mocked_get_request_param = mocker.patch.object(fake_base_view_obj, '_get_request_param')
        mocked_filter_param_name = mocker.patch.object(fake_base_view_obj, 'FILTER_PARAM_NAME')

        compared_filters = fake_base_view_obj.get_filters_from_request()
        expected_filters = mocked_get_request_param.return_value

        assert compared_filters == expected_filters

        mocked_get_request_param.assert_called_once_with(mocked_filter_param_name)


class TestBaseViewGetPage:
    def test_ok(self, mocker: MockFixture, fake_base_view_obj: BaseDataProviderView):
        mocked_get_request_param = mocker.patch.object(fake_base_view_obj, '_get_request_param')
        mocked_page_param_name = mocker.patch.object(fake_base_view_obj, 'PAGE_PARAM_NAME')

        compared_result = fake_base_view_obj.get_page_from_request()
        expected_result = mocked_get_request_param.return_value

        assert compared_result == expected_result

        mocked_get_request_param.assert_called_once_with(mocked_page_param_name)


class TestBaseViewGetInclude:
    def test_ok(self, mocker: MockFixture, fake_base_view_obj: BaseDataProviderView):
        mocked_get_request_param = mocker.patch.object(fake_base_view_obj, '_get_request_param')
        mocked_include_param_name = mocker.patch.object(fake_base_view_obj, 'INCLUDE_PARAM_NAME')

        compared_result = fake_base_view_obj.get_include_from_request()
        expected_result = mocked_get_request_param.return_value

        assert compared_result == expected_result

        mocked_get_request_param.assert_called_once_with(mocked_include_param_name)


class TestBaseViewGetRequestParam:
    def test_ok(self, mocker: MockFixture, fake_base_view_obj: BaseDataProviderView):
        fake_param_name = mocker. Mock()
        mocked_request = fake_base_view_obj._request = mocker.Mock()
        mocked_multidict = mocker.patch('aiohttp_baseapi.views.base.MultiDict')
        mocked_multidict_proxy = mocker.patch('aiohttp_baseapi.views.base.MultiDictProxy')

        compared_param = fake_base_view_obj._get_request_param(fake_param_name)
        expected_param = mocked_request.PARAMS.get.return_value.copy.return_value

        assert compared_param == expected_param

        mocked_multidict.assert_called_once()
        mocked_multidict_proxy.assert_called_once_with(mocked_multidict.return_value)
        mocked_request.PARAMS.get.assert_called_once_with(fake_param_name, mocked_multidict_proxy.return_value)
        mocked_request.PARAMS.get.return_value.copy.assert_called_once()
