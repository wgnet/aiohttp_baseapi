#!/usr/bin/env python
# flake8: noqa: E402
import argparse
import asyncio

from aiohttp import web

from conf import settings
from core.app import build_application

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Http API Worker', add_help=True)
    parser.add_argument('-p', '--port', required=False, default=settings.API_PORT, type=int,
                        help='port for http')
    parser.add_argument('--host', required=False, default=settings.API_HOST, type=str,
                        help='host for http')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()

    print('Starting application... \nLog level {}'.format(settings.LOGGING_LEVEL))

    web.run_app(build_application(loop), host=args.host, port=args.port)
