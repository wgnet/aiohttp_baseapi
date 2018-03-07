# -*- coding: utf-8 -*-

from aiohttp.web_exceptions import HTTPNotFound

from aiohttp_baseapi.decorators import jsonify_response
from aiohttp_baseapi.views.base import BaseDataProviderView


__all__ = (
    'BaseMeta',
    'BaseListView',
    'BaseEntityView',
)


class BaseMeta(BaseDataProviderView.Meta):
    body_data_schema = {
        'type': 'object',
        'properties': {
            'data': {}
        },
        'additionalProperties': False,
        'required': ['data']
    }


class BaseListView(BaseDataProviderView):
    @jsonify_response
    async def get(self):
        return await self.data_provider.get_many()

    @jsonify_response(status=201)
    async def post(self):
        await self.validate_body()
        data = self.body_data['data']
        new_entity = await self.data_provider.model.objects.insert(**data)
        return {
            'data': dict(new_entity)
        }


class BaseEntityView(BaseDataProviderView):
    def get_filters_from_request(self):
        filters = super().get_filters_from_request()
        filters.update({
            'id': self.request.match_info['id']
        })
        return filters

    async def _get_entity(self):
        entity = await self.data_provider.get_one()
        if not entity:
            raise HTTPNotFound()
        return self.data_provider.model(**entity)

    @jsonify_response
    async def get(self):
        item = await self.data_provider.get_one()
        if not item:
            raise HTTPNotFound()
        return item

    @jsonify_response(status=204)
    async def delete(self):
        entity = await self._get_entity()
        await entity.delete()

    @jsonify_response()
    async def put(self):
        entity = await self._get_entity()
        self.Meta.body_data_schema['properties']['data'].pop('required', None)
        await self.validate_body()
        new_data = self.body_data['data']
        await entity.update(**new_data)

        return {
            'data': dict(entity)
        }
