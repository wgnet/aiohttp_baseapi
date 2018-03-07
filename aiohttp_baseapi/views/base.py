# -*- coding: utf-8 -*-

import re
from json import JSONDecodeError

from aiohttp import web
from jsonschema import validate as validate_json, ValidationError
from multidict import MultiDict, MultiDictProxy

from aiohttp_baseapi.decorators import cachedproperty
from aiohttp_baseapi.errors import ApiError
from aiohttp_baseapi.views.exceptions import ViewValidationError, ViewError
from aiohttp_baseapi.log import logger


__all__ = (
    'BaseDataProviderView',
)


class BodyValidationViewMixin:

    body_data = None

    class Meta:
        body_data_schema = None
        multipart = False

    async def validate_body(self):
        if self.Meta.multipart:
            if self.request.content_type != 'multipart/form-data':
                logger.debug('Expected a multipart request but received "{}"'.format(self.request.content_type))
                error = ApiError().InvalidFormat('multipart/form-data content type is required')
                raise ViewError(errors=error)
            return

        if not self.Meta.body_data_schema:
            return

        try:
            data = await self.request.json()
        except JSONDecodeError as e:
            logger.debug('Bad request: {}, error: {}'.format(await self.request.text(), e.args))
            raise ViewError(errors=ApiError().InvalidFormat('Invalid json'))

        try:
            validate_json(data, self.Meta.body_data_schema)
        except ValidationError as e:
            logger.debug('Bad request data: {}, error: {}'.format(data, e.message))
            error = ApiError().InvalidDataSchema(e.message).Pointer(e.path)
            raise ViewValidationError(errors=error)

        self.body_data = data


class BaseDataProviderView(web.View, BodyValidationViewMixin):
    FIELDS_PARAM_NAME = 'fields'
    FILTER_PARAM_NAME = 'filter'
    PAGE_PARAM_NAME = 'page'
    INCLUDE_PARAM_NAME = 'include'
    SORT_PARAM_NAME = 'sort'

    MAX_LIMIT = 1000
    DEFAULT_LIMIT = 100
    DEFAULT_OFFSET = 0

    SORT_UP = 'asc'
    SORT_DOWN = 'desc'

    SORT_ORDERS = (SORT_UP, SORT_DOWN)

    DEFAULT_SORT_FIELD = None
    DEFAULT_SORT_ORDER = 'asc'

    class Meta(BodyValidationViewMixin.Meta):
        data_provider_class = None
        available_filters = []
        available_fields = []
        available_includes = {}
        available_sort_fields = []

    def __init__(self, request, fields=None, filters=None, page=None, sort=None, include=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        assert self.Meta.data_provider_class, 'Please, define data_provider.'

        self._fields = fields if fields is not None else self.get_fields_from_request() or {}
        self._filters = filters if filters is not None else self.get_filters_from_request() or {}
        self._page = page if page is not None else self.get_page_from_request() or {}
        self._sort = sort if sort is not None else self.get_sort_from_request() or {}
        self._include = include if include is not None else self.get_include_from_request() or {}

        self.validate_fields()
        self.validate_filters()
        self.validate_page()
        self.validate_includes()
        self.validate_sort()

    @property
    def available_fields(self):
        return self.Meta.available_fields

    @property
    def available_filters(self):
        return self.Meta.available_filters

    @property
    def available_sort_fields(self):
        return self.Meta.available_sort_fields

    @property
    def available_includes(self):
        return self.Meta.available_includes

    def validate_page(self):
        limit = self._page.get('limit', self.DEFAULT_LIMIT)
        offset = self._page.get('offset', self.DEFAULT_OFFSET)

        try:
            limit = int(limit)
        except ValueError:
            detail = 'Requested page limit "{}" is not integer.'.format(limit)
            error = ApiError().InvalidQueryParameter(detail).Parameter('page[limit]')
            raise ViewValidationError(errors=error)

        if limit > self.MAX_LIMIT:
            detail = 'Requested page limit "{}" is too big. Maximum is {}'.format(limit, self.MAX_LIMIT)
            error = ApiError().InvalidQueryParameter(detail).Parameter('page[limit]')
            raise ViewValidationError(errors=error)

        try:
            offset = int(offset)
        except ValueError:
            detail = 'Requested page offset "{}" is not integer.'.format(offset)
            error = ApiError().InvalidQueryParameter(detail).Parameter('page[offset]')
            raise ViewValidationError(errors=error)

        self._page.update({
            'limit': limit,
            'offset': offset,
        })

    def validate_fields(self):
        if not self._fields:
            return

        unavailable_fields = set(self._fields) - set(self.available_fields)
        if unavailable_fields:
            errors = []
            for field in unavailable_fields:
                detail = 'Requested field is not available - "{}"'.format(field)
                errors.append(ApiError().InvalidQueryParameter(detail).Parameter('fields'))
            raise ViewValidationError(errors=errors)

    def validate_filters(self):
        filter_keys = set([re.sub('__(lte|gte|ne)$', '', filter_key) for filter_key in self._filters.keys()])
        unavailable_filters = filter_keys - set(self.available_filters)
        if unavailable_filters:
            errors = []
            for filter_name in unavailable_filters:
                detail = 'Requested filter is not available - "{}"'.format(filter_name)
                errors.append(ApiError().InvalidQueryParameter(detail).Parameter('filter[{}]'.format(filter_name)))
            raise ViewValidationError(errors=errors)

        for filter_field, filter_value in self._filters.items():
            is_comparison_operator = filter_field.endswith('lte') or filter_field.endswith('gte')

            if is_comparison_operator and isinstance(filter_value, list):
                detail = 'Requested filter[{}] comparison operation not applied to list.'.format(filter_field)
                error = ApiError().InvalidFilterOperator(detail).Parameter('filter[{}]'.format(filter_field))
                raise ViewValidationError(errors=error)

    def validate_includes(self):
        unavailable_includes = set(self._include.keys()) - set(self.available_includes)
        if unavailable_includes:
            errors = []
            for include in unavailable_includes:
                detail = 'Requested include is not available - "{}"'.format(str(include))
                errors.append(ApiError().InvalidQueryParameter(detail).Parameter('include'))
            raise ViewValidationError(errors=errors)

        self._validate_include_params()

    def _validate_include_params(self):
        # We initialize include view right here to do all needed validation and build correct parameters
        include = dict()
        for include_name, params in self._include.items():
            view_class = self.Meta.available_includes[include_name]['view_class']
            view_init_params = dict(
                fields=params.get(self.FIELDS_PARAM_NAME, {}),
                filters=params.get(self.FILTER_PARAM_NAME, {}),
                page=params.get(self.PAGE_PARAM_NAME, {}),
                sort=params.get(self.SORT_PARAM_NAME, {}),
                include=params.get(self.INCLUDE_PARAM_NAME, {}),
            )
            # logger.debug('Init view "{}" with init params: {}'.format(view_class, view_init_params))

            view = view_class(self.request, **view_init_params)
            include_params = view.get_data_provider_params()
            include_data_provider_class = view.Meta.data_provider_class

            self.Meta.available_includes[include_name]['data_provider_class'] = include_data_provider_class
            include[include_name] = include_params
        self._include = include

    def validate_sort(self):
        if not self._sort:
            return

        clean_sort_fields = [sort_field.strip('-') for sort_field in self._sort]
        unavailable_sort_fields = set(clean_sort_fields) - set(self.available_sort_fields)
        if unavailable_sort_fields:
            errors = []
            for field in unavailable_sort_fields:
                detail = 'Requested sort field is not available - "{}"'.format(field)
                errors.append(ApiError().InvalidQueryParameter(detail).Parameter('sort'))
            raise ViewValidationError(errors=errors)

    @cachedproperty
    def data_provider(self):
        return self.Meta.data_provider_class(
            **self.get_data_provider_params()
        )

    def get_data_provider_params(self):
        return dict(
            fields=self._fields,
            filters=self._filters,
            include=self._include,
            page=self._page,
            sort=self._sort,
            available_includes=self.available_includes,
        )

    def get_fields_from_request(self) -> MultiDict:
        return self._get_request_param(self.FIELDS_PARAM_NAME)

    def get_filters_from_request(self) -> MultiDict:
        return self._get_request_param(self.FILTER_PARAM_NAME)

    def get_page_from_request(self) -> MultiDict:
        return self._get_request_param(self.PAGE_PARAM_NAME)

    def get_sort_from_request(self):
        return self._get_request_param(self.SORT_PARAM_NAME)

    def get_include_from_request(self) -> MultiDict:
        return self._get_request_param(self.INCLUDE_PARAM_NAME)

    def _get_request_param(self, param_name):
        param_immutable = self.request.PARAMS.get(param_name, MultiDictProxy(MultiDict()))

        return param_immutable.copy()
