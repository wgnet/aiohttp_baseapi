# -*- coding: utf-8 -*-

import re

from multidict import MultiDict, MultiDictProxy

__all__ = (
    'ParamsDict',
    'params_handler',
)


class ParamsDict(MultiDictProxy):
    """
    GET = {
        "filter[lang]": "en",
        "page[limit]": "100",
        "page[offset]": "50",

        "include": "child_1,child_1.child_1_1,child_1.child_1_2,child_2,child_2.child_2_1,child_2.child_2_2",
        "fields": "lang,child_1.lang,child_1.child_1_1.lang,child_1.child_1_2.lang,
                   child_2.lang,child_2.child_2_1.lang,child_2.child_2_2.lang",
        "sort": "created_at,-child_1.created_at,-child_1.child_1_1.created_at,child_1.child_1_2.created_at,
                 -child_2.created_at,child_2.child_2_1.created_at,-child_2.child_2_2.created_at",

        "filter[child_1.lang]": "en_1",
        "page[child_1.limit]": "100_1",
        "page[child_1.offset]": "50_1",

        "filter[child_1.child_1_1.lang]": "en_1_1",
        "page[child_1.child_1_1.limit]": "100_1_1",
        "page[child_1.child_1_1.offset]": "50_1_1",

        "filter[child_1.child_1_2.lang]": "en_1_2",
        "page[child_1.child_1_2.limit]": "100_1_2",
        "page[child_1.child_1_2.offset]": "50_1_2",

        "filter[child_2.lang]": "en_2",
        "page[child_2.limit]": "100_2",
        "page[child_2.offset]": "50_2",

        "filter[child_2.child_2_1.lang]": "en_2_1",
        "page[child_2.child_2_1.limit]": "100_2_1",
        "page[child_2.child_2_1.offset]": "50_2_1",

        "filter[child_2.child_2_2.lang]": "en_2_2",
        "page[child_2.child_2_2.limit]": "100_2_2",
        "page[child_2.child_2_2.offset]": "50_2_2",
    }

    print(ParamsDict(GET))

    {
        'include': {
            'child_1': {
                'include': {
                    'child_1_1': {
                        'fields': ['lang'],
                        'sort': ['-created_at'],
                        'filter': {'lang': 'en_1_1'},
                        'page': {'limit': '100_1_1', 'offset': '50_1_1'}
                    },
                    'child_1_2': {
                        'fields': ['lang'],
                        'sort': ['created_at'],
                        'filter': {'lang': 'en_1_2'},
                        'page': {'limit': '100_1_2', 'offset': '50_1_2'}
                    }
                },
                'fields': ['lang'],
                'sort': ['-created_at'],
                'filter': {'lang': 'en_1'},
                'page': {'limit': '100_1', 'offset': '50_1'}
            },
            'child_2': {
                'include': {
                    'child_2_1': {
                        'fields': ['lang'],
                        'sort': ['created_at'],
                        'filter': {'lang': 'en_2_1'},
                        'page': {'limit': '100_2_1', 'offset': '50_2_1'}
                    },
                    'child_2_2': {
                        'fields': ['lang'],
                        'sort': ['-created_at'],
                        'filter': {'lang': 'en_2_2'},
                        'page': {'limit': '100_2_2', 'offset': '50_2_2'}
                    }
                },
                'fields': ['lang'],
                'sort': ['-created_at'],
                'filter': {'lang': 'en_2'},
                'page': {'limit': '100_2', 'offset': '50_2'}
            }
        },
        'filter': {'lang': 'en'},
        'page': {'limit': '100', 'offset': '50'},
        'fields': ['lang'],
        'sort': ['created_at'],
    }
    """

    INCLUDE_PARAM = 'include'

    ENUMERATED_ENTITIES_FIELDS_PARAMS = ['fields', 'retrieve', 'sort']
    DICT_ENTITIES_FIELDS_PARAMS = ['filter', 'page']

    ALL_AVAILABLE_PARAMS = ENUMERATED_ENTITIES_FIELDS_PARAMS + DICT_ENTITIES_FIELDS_PARAMS

    VALUE_LIST_DELIMITER = ','
    ENTITY_PATH_DELIMITER = '.'
    FIELD_MODIFIERS = ['-']

    RE_FIELD_MODIFIERS = re.compile(
        '(?P<modifier>({}))'.format('|'.join(FIELD_MODIFIERS)),
        re.IGNORECASE
    )

    RE_PARAM_NAME = re.compile(
        '(?P<param_name>({}))'.format('|'.join(ALL_AVAILABLE_PARAMS)),
        re.IGNORECASE
    )

    RE_DICT_PATH = re.compile(
        '\[(?P<path>[^\]]+)\]',
        re.IGNORECASE
    )

    def __init__(self, GET):
        request = dict(GET)

        result_params = MultiDict()

        self.init_includes_tree(result_params, request)
        self.process_parameters(result_params, request)

        del request
        super().__init__(result_params)

    def init_includes_tree(self, result_params, request):
        for entity_path in request.pop(self.INCLUDE_PARAM, '').split(self.VALUE_LIST_DELIMITER):
            self.add_entity(result_params, entity_path)

    def process_parameters(self, result_params, request):
        # Now, walk over params, decide how to parse every one and save into the result params tree.
        # Notice: include is not in request already
        for raw_param, raw_value in request.items():
            match = self.RE_PARAM_NAME.match(raw_param)

            if not match:
                # it's an unknown parameter, ignore it
                continue

            param_name = match.group('param_name')

            if param_name in self.ENUMERATED_ENTITIES_FIELDS_PARAMS:
                self.process_enumerated_entities_fields_param(result_params, param_name, raw_value)
            elif param_name in self.DICT_ENTITIES_FIELDS_PARAMS:
                self.process_dict_entities_fields_params(result_params, param_name, raw_param, raw_value)

    def process_enumerated_entities_fields_param(self, result_params, param_name, raw_value):
        for raw_path in raw_value.split(self.VALUE_LIST_DELIMITER):
            entity_path, field = self.split_path_to_entity_and_field(raw_path)
            self.add_entity_field(result_params, entity_path, param_name, field)

    def process_dict_entities_fields_params(self, result_params, param_name, raw_param, raw_value):
        path_match = self.RE_DICT_PATH.search(raw_param)

        if not path_match:
            # dict without path inside?.. o_O...skip it
            return

        raw_path = path_match.group('path')
        value = self.prepare_value(raw_value)

        entity_path, field = self.split_path_to_entity_and_field(raw_path)
        self.add_param(result_params, entity_path, param_name, field, value)

    def add_entity(self, parent_node: MultiDict, path: [str, None]):
        if not path:
            # The end, we reached the leaf. All the includes have been initialized with empty dicts
            return

        current_include_name, rest_path = self.split_path_to_current_and_rest(path)
        current_node = parent_node.setdefault('include', MultiDict()).setdefault(current_include_name, MultiDict())

        self.add_entity(current_node, rest_path)

    def add_entity_field(self, parent_node: MultiDict, path: [str, None], param_name: str, field: str):
        if not path:
            # we reached the leaf. It's time to save param
            parent_node.setdefault(param_name, []).append(field)
            return

        # it is not the leaf, continue
        current_include_name, rest_path = self.split_path_to_current_and_rest(path)
        current_node = parent_node['include'].get(current_include_name)

        if current_node is None:
            # entity is not included. Ignore this param and do not save anywhere
            return

        self.add_entity_field(current_node, rest_path, param_name, field)

    def add_param(self, parent_node: MultiDict, path: [str, None], param_name: str, field: str, value: str):
        if not path:
            # we reached the leaf. It's time to save param
            parent_node.setdefault(param_name, MultiDict())[field] = value
            return

        # it is not the leaf, continue
        current_include_name, rest_path = self.split_path_to_current_and_rest(path)
        current_node = parent_node['include'].get(current_include_name)

        if current_node is None:
            # entity is not included. Ignore this param and do not save anywhere
            return

        self.add_param(current_node, rest_path, param_name, field, value)

    def split_path_to_entity_and_field(self, path: str):
        entity_path, field = path.rsplit(self.ENTITY_PATH_DELIMITER, 1) \
            if self.ENTITY_PATH_DELIMITER in path else (None, path)

        if entity_path is not None:
            match = self.RE_FIELD_MODIFIERS.match(entity_path)

            if match:
                modifier = match.group('modifier')
                field = '{}{}'.format(modifier, field)
                entity_path = entity_path[len(modifier):]

        return entity_path, field

    def split_path_to_current_and_rest(self, path: str):
        return path.split(self.ENTITY_PATH_DELIMITER, 1) if self.ENTITY_PATH_DELIMITER in path else (path, None)

    def prepare_value(self, raw_value: str):
        return raw_value.split(self.VALUE_LIST_DELIMITER) if self.VALUE_LIST_DELIMITER in raw_value else raw_value


async def params_handler(app, handler):
    async def handle(request):
        request.PARAMS = ParamsDict(request.query)

        return await handler(request)

    return handle
