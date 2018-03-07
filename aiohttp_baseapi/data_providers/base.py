# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
import asyncio

__all__ = (
    'BaseDataProvider',
)


class BaseDataProvider(ABC):
    """
    Base class for operating with data.

    Should be implemented methods:
     - get_data
     - get_total_count

    """

    def __init__(self, fields=None, filters=None, page=None, sort=None, include=None, available_includes=None):
        self._fields = fields or []
        self._filters = filters or {}
        self._page = page or {}
        self._sort = sort or {}
        self._include = include or {}
        self._available_includes = available_includes or {}

    async def get_filters(self):
        return dict(self._filters)

    def get_fields(self):
        return list(self._fields)

    async def get_limit(self):
        return self._page.get('limit')

    async def get_offset(self):
        return self._page.get('offset')

    async def get_sort(self):
        return self._sort

    @abstractmethod
    async def get_data(self) -> list:
        pass

    @abstractmethod
    async def get_total_count(self):
        pass

    async def get_meta(self):
        return {
            'total_count': await self.get_total_count(),
            'offset': await self.get_offset()
        }

    async def get_many(self) -> dict:
        """
        Returns structure:
        {
            "data": <list>,
            "meta": {
                "count": <int>,
                "total_count": <int>,
                "offset": <int>,
            }
        }
        """
        data = await self.get_data()
        meta = await self.get_meta()

        await asyncio.gather(*[
            self.extend_data_with_includes(data, name, params) for name, params in self._include.items()
        ])

        result = dict(data=data, meta=dict(count=len(data)))
        result['meta'].update(meta)

        return result

    async def get_one(self):
        data = await self.get_data()

        await asyncio.gather(*[
            self.extend_data_with_includes(data, name, params) for name, params in self._include.items()
        ])

        return data[0] if data else None

    async def extend_data_with_includes(self, data, include_name, include_params):
        include_data = await self.get_list_include_data(data, self._available_includes[include_name], include_params)
        self.update_with_include_data(data, include_name, include_data)

    @staticmethod
    def update_with_include_data(data, include_name, include_data):
        for i, item in enumerate(data):
            item.update({include_name: include_data[i]})

    async def get_list_include_data(self, data, include_settings, include_params):
        result = []

        for item in data:
            item_data = await self.get_item_include_data(item, include_settings, include_params)
            result.append(item_data)

        return result

    async def get_item_include_data(self, item, include_settings, include_params):
        filters = include_params.get('filters', {})

        assert 'relations' in include_settings, \
            'Improperly configured include: missing relations settings for %s' % \
            include_settings['data_provider_class'].__name__
        for relation in include_settings['relations']:
            root_field_name = relation['root_entity_field_name']
            root_field = item.get(root_field_name)
            if root_field is not None:
                filters[relation['included_entity_field_name']] = root_field
            else:
                filters[relation['included_entity_field_name']] = root_field_name

        init_params = dict(
            filters=filters,
            page=include_params.get('page'),
            sort=include_params.get('sort'),
            include=include_params.get('include'),
            available_includes=include_params.get('available_includes')
        )

        if 'data_provider_init_params' in include_settings:
            for init_param in include_settings['data_provider_init_params']:
                assert hasattr(self, init_param['attribute_name']), \
                    'Improperly configured include: missing init parameter %s for %s' % \
                    (init_param['attribute_name'], include_settings['data_provider_class'].__name__)
                init_params[init_param['param_name']] = getattr(self, init_param['attribute_name'])

        data_provider = include_settings['data_provider_class'](**init_params)

        return await data_provider.get_many()
