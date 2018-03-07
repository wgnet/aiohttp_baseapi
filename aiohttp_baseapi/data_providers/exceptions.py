# -*- coding: utf-8 -*-


class DataProviderError(Exception):
    pass


class DataProviderValidationError(DataProviderError):
    error = None

    def __init__(self, error=None):
        self.error = error if error is not None else {}

    def __str__(self, *args, **kwargs):
        return str(self.error)


class DataProviderNotFoundError(DataProviderError):
    pass
