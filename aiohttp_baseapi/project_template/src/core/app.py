# -*- coding: utf-8 -*-
import asyncio

from aiohttp import web

from conf import settings
from core import database
from core.middlewares import middlewares
from core.routes import urls

__all__ = (
    'Application',
    'build_application',
)


class Application(web.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = None
        self.on_shutdown.append(self.stop)

    async def setup(self):
        await database.setup(self)
        self.init_middlewares(middlewares)

    async def stop(self, app):
        app['db_engine'].close()
        await app['db_engine'].wait_closed()

    def init_middlewares(self, middlewares):
        for middleware in middlewares:
            self.middlewares.append(middleware)


def build_application(loop=None):
    loop = loop or asyncio.get_event_loop()
    app = Application(loop=loop, router=urls, debug=settings.DEBUG)

    loop.run_until_complete(app.setup())
    return app
