# -*- coding: utf-8 -*-

from aiohttp_baseapi.data_providers.model import ModelDataProvider

from apps.demo.models import Book, Author


class BooksDataProvider(ModelDataProvider):
    model = Book


class AuthorsDataProvider(ModelDataProvider):
    model = Author
