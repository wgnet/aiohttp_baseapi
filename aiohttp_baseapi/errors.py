# -*- coding: utf-8 -*-

import collections
from functools import partial

__all__ = (
    'ApiError',
)


class BaseModifier:
    error_obj = None

    def __init__(self, error_obj):
        self.error_obj = error_obj


class BaseErrorSource(BaseModifier):
    name = None

    def __call__(self, source):
        self.error_obj['source'] = {self.name: source}
        return self.error_obj


class BaseErrorType(BaseModifier):
    code = None

    def __call__(self, detail=None):
        self.error_obj['code'] = self.code

        if detail is not None:
            self.error_obj['detail'] = detail

        return self.error_obj


class Pointer(BaseErrorSource):
    name = 'pointer'

    PATH_DELIMITER = '/'

    def __call__(self, source):
        # if it's iterable and it's not a string, build the path
        if isinstance(source, collections.Iterable) and not isinstance(source, (str, bytes)):
            source = self.PATH_DELIMITER.join([str(part) for part in source])
        return super().__call__(source)


class Parameter(BaseErrorSource):
    name = 'parameter'


class BaseClientError(BaseErrorType):
    def __call__(self, code, detail=None):
        self.code = code.lower().replace(' ', '_')
        return super().__call__(detail)


class InvalidQueryParameter(BaseErrorType):
    code = 'invalid_query_parameter'


class UserIsBanned(BaseErrorType):
    code = 'user_is_banned'


class UnknownField(BaseErrorType):
    code = 'unknown_field'


class RequiredField(BaseErrorType):
    code = 'required_field'


class InvalidFormFieldValue(BaseErrorType):
    code = 'invalid_form_field_value'


class InternalError(BaseErrorType):
    code = 'internal_error'


class InvalidFormat(BaseErrorType):
    code = 'invalid_format'


class InvalidDataSchema(BaseErrorType):
    code = 'data_schema_validation_error'


class InvalidFilterOperator(BaseErrorType):
    code = 'invalid_filter_operator'


class InvalidSortOrder(BaseErrorType):
    code = 'invalid_sort_order'


class EntityNotFound(BaseErrorType):
    code = 'entity_not_found'


def callable_wrapper(klass, obj):
    return klass(obj)


def property_wrapper(klass):
    return property(partial(callable_wrapper, klass))


class ApiError(dict):
    """
        Usage code example:

        error = ApiError().InvalidQueryParameter('Api does not support includes').Parameter('include')
        error = ApiError().InvalidFieldValue().Pointer('ticket/fields_values/1')
    """

    Pointer = property_wrapper(Pointer)
    Parameter = property_wrapper(Parameter)

    InvalidQueryParameter = property_wrapper(InvalidQueryParameter)
    UserIsBanned = property_wrapper(UserIsBanned)
    UnknownField = property_wrapper(UnknownField)
    RequiredField = property_wrapper(RequiredField)
    InvalidFormFieldValue = property_wrapper(InvalidFormFieldValue)
    InternalError = property_wrapper(InternalError)
    InvalidFormat = property_wrapper(InvalidFormat)
    InvalidDataSchema = property_wrapper(InvalidDataSchema)
    InvalidFilterOperator = property_wrapper(InvalidFilterOperator)
    InvalidSortOrder = property_wrapper(InvalidSortOrder)
    EntityNotFound = property_wrapper(EntityNotFound)
    BaseClientError = property_wrapper(BaseClientError)
