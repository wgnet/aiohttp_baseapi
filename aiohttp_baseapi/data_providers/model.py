# -*- coding: utf-8 -*-

import asyncio
import operator as op
import re

from sqlalchemy.sql.operators import in_op
from sqlalchemy import select, func

from aiosqlalchemy_miniorm import BaseModelManager, OrderBy

from aiohttp_baseapi.data_providers.base import BaseDataProvider

__all__ = (
    'ComparisonFiltersMixin',
    'ModelDataProvider',
)


class ComparisonFiltersMixin:

    COMPARISON_OPERATOR_LTE = 'lte'
    COMPARISON_OPERATOR_GTE = 'gte'
    COMPARISON_OPERATOR_IN = 'in'
    COMPARISON_OPERATOR_EQ = 'eq'
    COMPARISON_OPERATOR_NE = 'ne'

    COMPARISON_SIGNS = '|'.join([
        COMPARISON_OPERATOR_LTE,
        COMPARISON_OPERATOR_GTE,
        COMPARISON_OPERATOR_NE
    ])

    filter_operators = {
        COMPARISON_OPERATOR_GTE: op.ge,
        COMPARISON_OPERATOR_LTE: op.le,
        COMPARISON_OPERATOR_EQ: op.eq,
        COMPARISON_OPERATOR_NE: op.ne,
        COMPARISON_OPERATOR_IN: in_op
    }

    def remove_comparison_suffix(self, filter_name):
        return re.sub('__({})$'.format(self.COMPARISON_SIGNS), '', filter_name)

    def get_comparison_operator(self, filter_name, filter_value):
        found_operator = re.search('__({})$'.format(self.COMPARISON_SIGNS), filter_name)

        if found_operator:
            return found_operator.group(1)

        return self.COMPARISON_OPERATOR_IN if isinstance(filter_value, list) else self.COMPARISON_OPERATOR_EQ


class ModelDataProvider(ComparisonFiltersMixin, BaseDataProvider):
    """
    A ready-to-use data provider working with database via aiosqlalchemy_miniorm.
    """

    model = None

    def _get_table_field(self, field_name):
        return getattr(self.model, self.remove_comparison_suffix(field_name))

    def get_field_where(self, field_name, field_value):
        operator = self.get_comparison_operator(field_name, field_value)

        return self.filter_operators[operator](self._get_table_field(field_name), field_value)

    async def get_sort(self):
        sort = []
        for sort_field in self._sort:
            sort_order = BaseModelManager.SORT_DOWN if sort_field.startswith('-') else BaseModelManager.SORT_UP
            sort.append(OrderBy(sort_field.strip('-'), sort_order))
        return sort

    async def get_sort_field(self):
        sort_list = await self.get_sort()
        if sort_list:
            return sort_list[0].field

    async def get_sort_order(self):
        sort_list = await self.get_sort()
        if sort_list:
            return sort_list[0].order

    def get_columns(self):
        fields = super().get_fields()

        if fields:
            return [self._get_table_field(field) for field in fields]

        return list(self.model.columns)

    async def get_where_list(self):
        result = []
        filters = await self.get_filters()

        for filter_field, filter_value in filters.items():
            if hasattr(self.model, self.remove_comparison_suffix(filter_field)):
                result.append(self.get_field_where(filter_field, filter_value))

        return result

    def _get_query(self):
        return select(self.get_columns()).select_from(self.model.table)

    async def get_data(self):
        rows = await self.model.objects.get_items(
            query=self._get_query(),
            where_list=await self.get_where_list(),
            limit=await self.get_limit(),
            offset=await self.get_offset(),
            order_by=await self.get_sort()
        )

        return [dict(row) for row in rows]

    async def get_total_count(self):
        return await self.model.objects.count(
            query=self._get_query().with_only_columns([func.count(self.model.pk_column)]),
            where_list=await self.get_where_list()
        )

    async def get_list_include_data(self, data, include_settings, include_params):
        return await asyncio.gather(*[
            self.get_item_include_data(item, include_settings, include_params) for item in data
        ])
