# -*- coding: utf-8 -*-

import pytest
from asynctest import CoroutineMock

from aiohttp_baseapi.middleware.params_handler import (
    params_handler as factory,
    ParamsDict
)


@pytest.fixture
def mocked_super_init(mocker):
    return mocker.Mock(return_value=None)


@pytest.fixture
def fake_params_dict():
    class FakeParamsDict(ParamsDict):
        def __init__(self):
            self._request = {}
            self._dict_params_names = []

    return FakeParamsDict()


class TestOverallOnSamples:
    @pytest.mark.asyncio
    @pytest.mark.parametrize('input, expected_output', [

        # without includes
        ({
            "filter[campaign_id]": "1,2,3",
            "filter[role]": "recruit",
            "page[limit]": "10",
            "fields": "role,campaign_id",
            "sort": "created_at"
        }, {
            "filter": {
                "campaign_id": ["1", "2", "3"],
                "role": "recruit"
            },
            "page": {
                "limit": "10"
            },
            "fields": ["role", "campaign_id"],
            "sort": ["created_at"],
        }),

        # with one include
        ({
            "filter[campaign_id]": "1,2,3",
            "filter[role]": "recruit",
            "page[limit]": "10",
            "fields": "role,campaign_id,attributes.name,attributes.value",
            "sort": "created_at,-attributes.name",

            "include": "attributes",
            "filter[attributes.id]": "1,2,3",
            "filter[attributes.lang]": "en",
            "page[attributes.limit]": "20",
        }, {
            "filter": {
                "campaign_id": ["1", "2", "3"],
                "role": "recruit"
            },
            "page": {
                "limit": "10",
            },
            "fields": ["role", "campaign_id"],
            "sort": ["created_at"],
            "include": {
                "attributes": {
                    "filter": {
                        "id": ["1", "2", "3"],
                        "lang": "en"
                    },
                    "page": {
                        "limit": "20"
                    },
                    "fields": ["name", "value"],
                    "sort": ["-name"],
                }
            }
        }),

        # with several includes
        ({
            "filter[key]": "1",
            "retrieve": "data,some1.meta,some2.meta",
            "include": "some1,some2",
            "filter[some1.key]": "1,2,3",
            "filter[some2.key]": "3,2,1",
        }, {
            "filter": {
                "key": "1"
            },
            "retrieve": ["data"],
            "include": {
                "some1": {
                    "filter": {
                        "key": ["1", "2", "3"],
                    },
                    "retrieve": ["meta"]
                },
                "some2": {
                    "filter": {
                        "key": ["3", "2", "1"],
                    },
                    "retrieve": ["meta"]
                }
            }
        }),

        # with includes in includes
        ({
            "filter[key]": "1",
            "retrieve": "data,some1.meta,some2.meta",
            "include": "some1,some2,some1.some3,some1.some3.some4,some1.some3.some5",
            "filter[some1.key]": "1,2,3",
            "filter[some2.key]": "3,2,1",
        }, {
            "filter": {
                "key": "1"
            },
            "retrieve": ["data"],
            "include": {
                "some1": {
                    "include": {
                        "some3": {
                            "include": {
                                "some4": {},
                                "some5": {},
                            }
                        }
                    },
                    "filter": {
                        "key": ["1", "2", "3"],
                    },
                    "retrieve": ["meta"]
                },
                "some2": {
                    "filter": {
                        "key": ["3", "2", "1"],
                    },
                    "retrieve": ["meta"]
                }
            }
        }),
    ])
    async def test_ok(self, input, expected_output):
        assert dict(ParamsDict(input)) == expected_output


class TestParamsHandler:
    @pytest.mark.asyncio
    async def test_ok(self, mocker):
        fake_app = mocker.Mock()
        fake_handler = CoroutineMock()
        fake_request = mocker.Mock()
        mocked_params_dict = mocker.patch('aiohttp_baseapi.middleware.params_handler.ParamsDict')

        handle_func = await factory(fake_app, fake_handler)
        await handle_func(fake_request)

        fake_handler.assert_called_once_with(fake_request)
        mocked_params_dict.assert_called_once_with(fake_request.query)
