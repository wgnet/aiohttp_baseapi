# -*- coding: utf-8 -*-
import os
from glob import glob
from importlib import import_module

from aiopg.sa import create_engine
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

from aiosqlalchemy_miniorm import RowModel, RowModelDeclarativeMeta

from conf import settings
from core.log import logger

metadata = MetaData()
BaseModel = declarative_base(metadata=metadata, cls=RowModel, metaclass=RowModelDeclarativeMeta)


async def get_db_engine():
    return await create_engine(
        user=settings.DATABASE['user'],
        database=settings.DATABASE['database'],
        host=settings.DATABASE['host'],
        port=settings.DATABASE['port'],
        password=settings.DATABASE['password'],
        minsize=settings.DATABASE['minsize'],
        maxsize=settings.DATABASE['maxsize'],
        echo=settings.DEBUG,
    )


async def setup(app=None):
    engine = await get_db_engine()

    if app is not None:
        app['db_engine'] = engine

    metadata.bind = engine


def init_models():
    for path in glob(settings.MODELS_PATTERN, recursive=True):
        path = os.path.splitext(path)[0]
        path = path.strip('./').replace('/', '.')
        try:
            import_module(path)
        except ImportError as e:
            logger.warning('models module %s not found' % path, str(e))
