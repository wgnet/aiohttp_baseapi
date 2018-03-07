# -*- coding: utf-8 -*-

import pytest
from asynctest import CoroutineMock
from pytest_mock import MockFixture

from aiohttp_baseapi.data_providers.base import (
    BaseDataProvider,
)


@pytest.fixture
def fake_data_provider_cls():
    class FakeDataProviderCls(BaseDataProvider):
        async def get_data(self):
            pass

        async def get_total_count(self):
            pass

    return FakeDataProviderCls


@pytest.fixture
def fake_data_provider(mocker: MockFixture, fake_data_provider_cls):
    return fake_data_provider_cls()


class TestBaseDataProviderInit:
    def test_ok(self, mocker: MockFixture, fake_data_provider_cls):
        fake_filters = mocker.Mock()
        fake_page = mocker.Mock()
        fake_sort = mocker.Mock()
        fake_include = mocker.Mock()
        fake_available_includes = mocker.Mock()

        base_data_provider = fake_data_provider_cls(
            filters=fake_filters,
            page=fake_page,
            sort=fake_sort,
            include=fake_include,
            available_includes=fake_available_includes
        )

        assert base_data_provider._filters == fake_filters
        assert base_data_provider._page == fake_page
        assert base_data_provider._sort == fake_sort
        assert base_data_provider._include == fake_include
        assert base_data_provider._available_includes == fake_available_includes


class TestBaseDataProviderGetMeta:
    @pytest.mark.asyncio
    async def test_ok(self, mocker: MockFixture, fake_data_provider: BaseDataProvider):
        mocked_get_total_count = mocker.patch.object(fake_data_provider, 'get_total_count', CoroutineMock())
        mocked_get_offset = mocker.patch.object(fake_data_provider, 'get_offset', CoroutineMock())

        compared_meta = await fake_data_provider.get_meta()
        expected_meta = dict(
            total_count=mocked_get_total_count.return_value,
            offset=mocked_get_offset.return_value
        )

        assert compared_meta == expected_meta

        mocked_get_total_count.assert_called_once()
        mocked_get_offset.assert_called_once()


class TestBaseDataProviderGetMany:
    @pytest.mark.asyncio
    async def test_ok(self, mocker: MockFixture, fake_data_provider: BaseDataProvider):
        mocked_get_data = mocker.patch.object(fake_data_provider, 'get_data', CoroutineMock(return_value=[1, 2, 3]))
        mocked_get_meta = mocker.patch.object(fake_data_provider, 'get_meta', CoroutineMock(return_value={'foo': 123}))
        mocker.patch.object(fake_data_provider, '_include', {'baz': 'bar'})
        mocked_extend_data_with_includes = mocker.patch.object(
            fake_data_provider,
            'extend_data_with_includes',
            CoroutineMock()
        )

        compared_many = await fake_data_provider.get_many()
        expected_many = dict(data=mocked_get_data.return_value, meta=dict(count=3, foo=123))

        assert compared_many == expected_many

        mocked_get_data.assert_called_once_with()
        mocked_get_meta.assert_called_once_with()
        mocked_extend_data_with_includes.assert_called_once_with(mocked_get_data.return_value, 'baz', 'bar')


class TestBaseDataProviderGetOne:
    @pytest.mark.asyncio
    async def test_ok(self, mocker: MockFixture, fake_data_provider: BaseDataProvider):
        mocked_get_data = mocker.patch.object(
            fake_data_provider, 'get_data', CoroutineMock(return_value=[mocker.Mock()])
        )
        mocker.patch.object(fake_data_provider, '_include', {'baz': 'bar'})
        mocked_extend_data_with_includes = mocker.patch.object(
            fake_data_provider,
            'extend_data_with_includes',
            CoroutineMock()
        )

        compared_one = await fake_data_provider.get_one()
        expected_one = mocked_get_data.return_value[0]

        assert compared_one == expected_one
        mocked_extend_data_with_includes.assert_called_once_with(mocked_get_data.return_value, 'baz', 'bar')

    @pytest.mark.asyncio
    async def test_ok_no_results(self, mocker: MockFixture, fake_data_provider: BaseDataProvider):
        mocker.patch.object(fake_data_provider, 'get_data', CoroutineMock(return_value=None))

        compared_one = await fake_data_provider.get_one()
        expected_one = None

        assert compared_one == expected_one


class TestBaseDataProviderExtendDataWithIncludes:
    @pytest.mark.asyncio
    async def test_ok(self, mocker: MockFixture, fake_data_provider: BaseDataProvider):
        fake_data = mocker.Mock()
        fake_include_name = 'foo'
        fake_include_params = mocker.Mock()
        mocker.patch.object(fake_data_provider, '_available_includes', {fake_include_name: 'bar'})
        mocked_update_with_include_data = mocker.patch.object(fake_data_provider, 'update_with_include_data')
        mocked_get_list_include_data = mocker.patch.object(
            fake_data_provider,
            'get_list_include_data',
            CoroutineMock()
        )

        await fake_data_provider.extend_data_with_includes(fake_data, fake_include_name, fake_include_params)

        mocked_get_list_include_data.assert_called_once_with(fake_data, 'bar', fake_include_params)
        mocked_update_with_include_data.assert_called_once_with(
            fake_data,
            fake_include_name,
            mocked_get_list_include_data.return_value
        )


class TestBaseDataProviderUpdateWithIncludeData:
    @pytest.mark.parametrize('fake_data, fake_include_data, expected_result_data', [
        (
            [{'existing_key': 'existing_value'}],
            [{'foo': 'bar'}],
            [
                {
                    'existing_key': 'existing_value',
                    'NAME': {
                        'foo': 'bar'
                    }
                }
            ]
        ),

        (
            [{'existing_key1': 'existing_value1'}, {'existing_key2': 'existing_value2'}],
            [{'foo1': 'bar1'}, {'foo2': 'bar2'}],
            [
                {
                    'existing_key1': 'existing_value1',
                    'NAME': {
                        'foo1': 'bar1'
                    }
                },
                {
                    'existing_key2': 'existing_value2',
                    'NAME': {
                        'foo2': 'bar2'
                    }
                }
            ]
        )
    ])
    def test_on_samples(self, fake_data, fake_include_data, expected_result_data, fake_data_provider):
        fake_data_provider.update_with_include_data(fake_data, 'NAME', fake_include_data)
        assert fake_data == expected_result_data


class TestBaseDataProviderGetListIncludeData:
    @pytest.mark.asyncio
    async def test_ok(self, mocker: MockFixture, fake_data_provider: BaseDataProvider):
        data_length = 10
        fake_data = [mocker.Mock() for _ in range(0, data_length)]
        fake_include_settings = mocker.Mock()
        fake_include_params = mocker.Mock()
        fake_item_include_data = mocker.Mock()
        mocked_get_item_include_data = mocker.patch.object(
            fake_data_provider,
            'get_item_include_data',
            CoroutineMock(return_value=fake_item_include_data)
        )

        result = await fake_data_provider.get_list_include_data(fake_data, fake_include_settings, fake_include_params)

        mocked_get_item_include_data.assert_has_calls([
            mocker.call(fake_data[i], fake_include_settings, fake_include_params) for i in range(0, data_length)
        ])
        assert result == [fake_item_include_data for _ in range(0, data_length)]


class TestBaseDataProviderGetItemIncludeData:
    @pytest.mark.asyncio
    async def test_ok(self, mocker: MockFixture, fake_data_provider: BaseDataProvider):
        fake_get_many = CoroutineMock()
        fake_data_provider.test_attribute_name = 'test_attribute_value'
        fake_include_settings_data_provider = mocker.Mock(
            __name__='foo',
            return_value=mocker.Mock(get_many=fake_get_many)
        )
        fake_item = mocker.Mock()
        fake_include_settings = {
            'relations': [{
                'included_entity_field_name': 'foo',
                'root_entity_field_name': 'bar',
            }],
            'data_provider_init_params': [{
                'param_name': 'test_param_name',
                'attribute_name': 'test_attribute_name',
            }],
            'data_provider_class': fake_include_settings_data_provider
        }
        fake_include_params = {
            'page': mocker.Mock(),
            'sort': mocker.Mock(),
            'available_includes': mocker.Mock(),
            'include': mocker.Mock(),
        }

        result = await fake_data_provider.get_item_include_data(fake_item, fake_include_settings, fake_include_params)

        fake_item.get.assert_called_once_with('bar')
        fake_include_settings_data_provider.assert_called_once_with(
            filters={'foo': fake_item.get.return_value},
            page=fake_include_params.get('page'),
            sort=fake_include_params.get('sort'),
            include=fake_include_params.get('include'),
            available_includes=fake_include_params.get('available_includes'),
            test_param_name='test_attribute_value'
        )
        fake_get_many.assert_called_once_with()
        assert result == fake_get_many.return_value

    @pytest.mark.asyncio
    async def test_relations_assertion(self, mocker: MockFixture, fake_data_provider: BaseDataProvider):
        fake_get_many = CoroutineMock()
        fake_include_settings_data_provider = mocker.Mock(
            __name__='foo',
            return_value=mocker.Mock(get_many=fake_get_many)
        )
        fake_item = mocker.Mock()
        fake_include_settings = {
            'data_provider_class': fake_include_settings_data_provider
        }
        fake_include_params = {'page': mocker.Mock(), 'fields': mocker.Mock()}

        with pytest.raises(AssertionError):
            await fake_data_provider.get_item_include_data(fake_item, fake_include_settings, fake_include_params)

        fake_item.get.assert_not_called()
        fake_include_settings_data_provider.assert_not_called()
        fake_get_many.assert_not_called()

    @pytest.mark.asyncio
    async def test_init_params_assertion(self, mocker: MockFixture, fake_data_provider: BaseDataProvider):
        fake_get_many = CoroutineMock()
        fake_include_settings_data_provider = mocker.Mock(
            __name__='foo',
            return_value=mocker.Mock(get_many=fake_get_many)
        )
        fake_item = mocker.Mock()
        fake_include_settings = {
            'relations': [{
                'included_entity_field_name': 'foo',
                'root_entity_field_name': 'bar',
            }],
            'data_provider_init_params': [{
                'param_name': 'wrong_param_name',
                'attribute_name': 'test_attribute_name',
            }],
            'data_provider_class': fake_include_settings_data_provider
        }
        fake_include_params = {'page': mocker.Mock(), 'fields': mocker.Mock()}

        with pytest.raises(AssertionError):
            await fake_data_provider.get_item_include_data(fake_item, fake_include_settings, fake_include_params)

        fake_item.get.assert_called_once_with('bar')
        fake_include_settings_data_provider.assert_not_called()
        fake_get_many.assert_not_called()
