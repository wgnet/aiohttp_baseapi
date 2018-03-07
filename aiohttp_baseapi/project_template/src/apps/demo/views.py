# -*- coding: utf-8 -*-

from alchemyjsonschema import SchemaFactory, ForeignKeyWalker

from core.views import BaseListView, BaseEntityView, BaseMeta

from apps.demo.models import Book, Author
from apps.demo.data_providers import BooksDataProvider, AuthorsDataProvider


model_schema = SchemaFactory(ForeignKeyWalker)


class BaseAuthorsMeta(BaseMeta):
    data_provider_class = AuthorsDataProvider
    body_data_schema = dict(BaseMeta.body_data_schema, properties={'data': model_schema(Author, excludes=['id'])})


class AuthorsListView(BaseListView):
    class Meta(BaseAuthorsMeta):
        available_filters = ['id', 'name', 'surname']
        available_fields = ['name', 'surname']
        available_sort_fields = ['name', 'surname']


class AuthorByIdView(BaseEntityView):
    class Meta(BaseAuthorsMeta):
        available_filters = ['id']


class BaseBooksMeta(BaseMeta):
    data_provider_class = BooksDataProvider
    body_data_schema = dict(BaseMeta.body_data_schema, properties={'data': model_schema(Book, excludes=['id'])})


class BooksListView(BaseListView):
    class Meta(BaseBooksMeta):
        available_filters = ['id', 'category', 'name', 'is_available']
        available_fields = ['category', 'name', 'is_available']
        available_includes = {
            'authors': {
                'view_class': AuthorsListView,
                'relations': [{
                    'included_entity_field_name': Author.id.name,
                    'root_entity_field_name': Book.author_id.name,
                }],
            }
        }
        available_sort_fields = ['category', 'name', 'is_available']


class BookByIdView(BaseEntityView):
    class Meta(BaseBooksMeta):
        available_filters = ['id']
