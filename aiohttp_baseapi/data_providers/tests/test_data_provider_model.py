# -*- coding: utf-8 -*-

import pytest
from asynctest import CoroutineMock
from pytest_mock import MockFixture
from aiosqlalchemy_miniorm import OrderBy

from aiohttp_baseapi.data_providers.model import (
    ModelDataProvider
)


@pytest.fixture
def fake_model_data_provider(mocker: MockFixture):
    return ModelDataProvider()


class TestModelDataProviderRemoveComparisonSuffix:
    @pytest.mark.asyncio
    async def test_ok(self, mocker: MockFixture, fake_model_data_provider: ModelDataProvider):
        fake_filter_name = mocker.Mock()
        mocked_sub = mocker.patch('re.sub')

        compared_result = fake_model_data_provider.remove_comparison_suffix(fake_filter_name)
        expected_result = mocked_sub.return_value

        assert compared_result == expected_result

        mocked_sub.assert_called_once_with(
            '__({})$'.format(fake_model_data_provider.COMPARISON_SIGNS),
            '',
            fake_filter_name
        )


class TestBaseDataProviderGetComparisonOperator:
    @pytest.mark.asyncio
    async def test_ok_eq(self, mocker: MockFixture, fake_model_data_provider: ModelDataProvider):
        fake_filter_name = mocker.Mock()
        fake_filter_value = mocker.Mock(spec=str)
        fake_eq = mocker.patch.object(fake_model_data_provider, 'COMPARISON_OPERATOR_EQ')
        mocked_search = mocker.patch('re.search', return_value=None)

        compared_operator = fake_model_data_provider.get_comparison_operator(fake_filter_name, fake_filter_value)
        expected_operator = fake_eq

        assert compared_operator == expected_operator

        mocked_search.assert_called_once_with(
            '__({})$'.format(fake_model_data_provider.COMPARISON_SIGNS),
            fake_filter_name
        )

    @pytest.mark.asyncio
    async def test_ok_in(self, mocker: MockFixture, fake_model_data_provider: ModelDataProvider):
        fake_filter_name = mocker.Mock()
        fake_filter_value = mocker.Mock(spec=list)
        fake_in = mocker.patch.object(fake_model_data_provider, 'COMPARISON_OPERATOR_IN')
        mocked_search = mocker.patch('re.search', return_value=None)

        compared_operator = fake_model_data_provider.get_comparison_operator(fake_filter_name, fake_filter_value)
        expected_operator = fake_in

        assert compared_operator == expected_operator

        mocked_search.assert_called_once_with(
            '__({})$'.format(fake_model_data_provider.COMPARISON_SIGNS),
            fake_filter_name
        )

    @pytest.mark.asyncio
    async def test_ok_signs(self, mocker: MockFixture, fake_model_data_provider: ModelDataProvider):
        fake_filter_name = mocker.Mock()
        fake_filter_value = mocker.Mock()
        mocked_search = mocker.patch('re.search')

        compared_operator = fake_model_data_provider.get_comparison_operator(fake_filter_name, fake_filter_value)
        expected_operator = mocked_search.return_value.group.return_value

        assert compared_operator == expected_operator

        mocked_search.assert_called_once_with(
            '__({})$'.format(fake_model_data_provider.COMPARISON_SIGNS),
            fake_filter_name
        )
        mocked_search.return_value.group.assert_called_once_with(1)


class TestModelDataProviderGetTableField:
    def test_ok(self, mocker: MockFixture, fake_model_data_provider: ModelDataProvider):
        fake_model = mocker.patch.object(fake_model_data_provider, 'model')
        fake_field_name = 'test'
        mocked_remove_comparison_suffix = mocker.patch.object(
            fake_model_data_provider,
            'remove_comparison_suffix',
            return_value=fake_field_name
        )

        compared_field = fake_model_data_provider._get_table_field(fake_field_name)
        expected_field = getattr(fake_model, mocked_remove_comparison_suffix.return_value)

        assert compared_field == expected_field
        mocked_remove_comparison_suffix.assert_called_once_with(fake_field_name)


class TestModelDataProviderGetFieldWhere:
    def test_ok(self, mocker: MockFixture, fake_model_data_provider: ModelDataProvider):
        fake_field_name = mocker.Mock()
        fake_field_value = mocker.Mock()
        fake_operator = 'test_operator'
        fake_operator_func = mocker.Mock()
        mocker.patch.object(fake_model_data_provider, 'filter_operators', dict(test_operator=fake_operator_func))
        mocked_get_comparison_operator = mocker.patch.object(
            fake_model_data_provider,
            'get_comparison_operator',
            return_value=fake_operator
        )
        mocked_get_table_field = mocker.patch.object(fake_model_data_provider, '_get_table_field')

        compared_field_where = fake_model_data_provider.get_field_where(fake_field_name, fake_field_value)
        expected_field_where = fake_operator_func.return_value

        assert compared_field_where == expected_field_where

        mocked_get_comparison_operator.assert_called_once_with(fake_field_name, fake_field_value)
        mocked_get_table_field.assert_called_once_with(fake_field_name)
        fake_operator_func.assert_called_once_with(
            mocked_get_table_field.return_value,
            fake_field_value
        )


class TestModelDataProviderGetWhereList:
    @pytest.mark.asyncio
    async def test_ok_filter_value_is_not_list(self, mocker: MockFixture, fake_model_data_provider: ModelDataProvider):
        fake_filters = dict(test=mocker.Mock())
        mocked_hasattr = mocker.patch('aiohttp_baseapi.data_providers.model.hasattr', mocker.Mock(return_value=True))

        mocked_get_table_field = mocker.patch.object(fake_model_data_provider, '_get_table_field')
        mocked_remove_comparison_suffix = mocker.patch.object(fake_model_data_provider, 'remove_comparison_suffix')
        mocked_get_filters = mocker.patch.object(
            fake_model_data_provider, 'get_filters', CoroutineMock(return_value=fake_filters)
        )

        compared_where_list = await fake_model_data_provider.get_where_list()

        expected_where_list = [
            (mocked_get_table_field.return_value == filter_value) for filter_value in fake_filters.values()
        ]
        assert compared_where_list == expected_where_list
        mocked_get_table_field.has_calls([mocker.call(filter_name) for filter_name in fake_filters.keys()])
        mocked_remove_comparison_suffix.has_calls([mocker.call(filter_value) for filter_value in fake_filters.values()])
        mocked_hasattr.has_calls(
            [mocker.call(fake_model_data_provider.model, mocked_remove_comparison_suffix.return_value)
             for _ in fake_filters.keys()]
        )
        mocked_get_filters.assert_called_once()

    @pytest.mark.asyncio
    async def test_ok_filter_values_is_list(self, mocker: MockFixture, fake_model_data_provider: ModelDataProvider):
        fake_filters = dict(test=[mocker.Mock()])
        mocked_hasattr = mocker.patch('aiohttp_baseapi.data_providers.model.hasattr', mocker.Mock(return_value=True))
        mocked_remove_comparison_suffix = mocker.patch.object(fake_model_data_provider, 'remove_comparison_suffix')
        mocked_get_table_field = mocker.patch.object(fake_model_data_provider, '_get_table_field')
        mocked_get_filters = mocker.patch.object(
            fake_model_data_provider, 'get_filters', CoroutineMock(return_value=fake_filters)
        )

        compared_where_list = await fake_model_data_provider.get_where_list()
        expected_where_list = [
            mocked_get_table_field.return_value.in_.return_value for _ in fake_filters.values()
        ]
        expected_filter_calls = [mocker.call(filter_name) for filter_name in fake_filters.keys()]
        expected_in_calls = [mocker.call(filter_value) for filter_value in fake_filters.values()]

        assert compared_where_list == expected_where_list

        mocked_get_table_field.has_calls(expected_filter_calls, any_order=True)
        mocked_get_table_field.return_value.in_.has_calls(expected_in_calls, any_order=True)
        mocked_remove_comparison_suffix.has_calls([mocker.call(filter_value) for filter_value in fake_filters.values()])
        mocked_hasattr.has_calls(
            [mocker.call(fake_model_data_provider.model, mocked_remove_comparison_suffix.return_value)
             for _ in fake_filters.keys()]
        )
        mocked_get_filters.assert_called_once()


class TestModelDataProviderGetData:
    @pytest.mark.asyncio
    async def test_ok(self, mocker: MockFixture, fake_model_data_provider: ModelDataProvider):
        fake_results = [dict(test=mocker.Mock())]
        mocked_model = mocker.patch.object(fake_model_data_provider, 'model', CoroutineMock(**{
            'objects.get_items.return_value': fake_results
        }))
        mocked_get_where_list = mocker.patch.object(fake_model_data_provider, 'get_where_list', CoroutineMock())
        mocked_get_limit = mocker.patch.object(fake_model_data_provider, 'get_limit', CoroutineMock())
        mocked_get_offset = mocker.patch.object(fake_model_data_provider, 'get_offset', CoroutineMock())
        mocked_get_query = mocker.patch.object(fake_model_data_provider, '_get_query', mocker.Mock())
        mocked_get_sort = mocker.patch.object(fake_model_data_provider, 'get_sort', CoroutineMock())

        compared_results = await fake_model_data_provider.get_data()

        assert compared_results == fake_results

        mocked_get_query.assert_called_once()
        mocked_get_where_list.assert_called_once()
        mocked_get_limit.assert_called_once()
        mocked_get_offset.assert_called_once()
        mocked_get_sort.assert_called_once()

        mocked_model.objects.get_items.assert_called_once_with(
            query=mocked_get_query.return_value,
            where_list=mocked_get_where_list.return_value,
            limit=mocked_get_limit.return_value,
            offset=mocked_get_offset.return_value,
            order_by=mocked_get_sort.return_value
        )


class TestModelDataProviderGetTotalCount:
    @pytest.mark.asyncio
    async def test_ok(self, mocker: MockFixture, fake_model_data_provider: ModelDataProvider):
        fake_count = mocker.Mock()
        mocked_get_query = mocker.patch.object(fake_model_data_provider, '_get_query')
        mocked_sa_func_count = mocker.patch('aiohttp_baseapi.data_providers.model.func.count')
        mocked_model = mocker.patch.object(fake_model_data_provider, 'model', CoroutineMock(**{
            'objects.count.return_value': fake_count,
            'pk_column': mocker.Mock()
        }))
        mocked_get_where_list = mocker.patch.object(fake_model_data_provider, 'get_where_list', CoroutineMock())

        compared_count = await fake_model_data_provider.get_total_count()

        assert compared_count == fake_count

        mocked_get_where_list.assert_called_once()
        mocked_model.objects.count.assert_called_once_with(
            query=mocked_get_query.return_value.with_only_columns.return_value,
            where_list=mocked_get_where_list.return_value
        )
        mocked_get_query.return_value.with_only_columns.assert_called_once_with([mocked_sa_func_count.return_value])
        mocked_sa_func_count.assert_called_once_with(mocked_model.pk_column)


class TestModelDataProviderGetListIncludeData:
    @pytest.mark.asyncio
    async def test_ok(self, mocker: MockFixture, fake_model_data_provider: ModelDataProvider):
        data_length = 10
        fake_data = [mocker.Mock() for _ in range(0, data_length)]
        fake_include_settings = mocker.Mock()
        fake_include_params = mocker.Mock()
        fake_item_include_data = mocker.Mock()
        mocked_get_item_include_data = mocker.patch.object(
            fake_model_data_provider,
            'get_item_include_data',
            CoroutineMock(return_value=fake_item_include_data)
        )

        result = await fake_model_data_provider.get_list_include_data(
            fake_data,
            fake_include_settings,
            fake_include_params
        )

        mocked_get_item_include_data.assert_has_calls([
            mocker.call(fake_data[i], fake_include_settings, fake_include_params) for i in range(0, data_length)
        ])
        assert result == [fake_item_include_data for _ in range(0, data_length)]


class TestModelDataProviderGetSort:
    @pytest.mark.asyncio
    async def test_ok(self, mocker: MockFixture, fake_model_data_provider: ModelDataProvider):
        mocker.patch.object(fake_model_data_provider, '_sort', new=['foo', '-bar'])
        result = await fake_model_data_provider.get_sort()

        assert result == [OrderBy('foo', 'asc'), OrderBy('bar', 'desc',)]
