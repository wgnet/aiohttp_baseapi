# -*- coding: utf-8 -*-
from core.dispatcher import SmartUrlDispatcher

from apps.default.routes import urls as default_urls
from apps.demo.routes import urls as demo_urls

__all__ = (
    'urls',
)

urls = SmartUrlDispatcher()

urls.include(default_urls)
urls.include(demo_urls)
