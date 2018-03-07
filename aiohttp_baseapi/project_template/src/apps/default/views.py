from aiohttp import web


class DefaultView(web.View):
    async def get(self):
        registred_urls = []

        for resource in self.request.app.router.resources():
            for route in list(resource):
                if route.method == 'OPTIONS':
                    continue
                info = resource.get_info()
                registred_urls.append({
                    'method': route.method,
                    'url': info.get('path') or info.get('formatter')
                })
        return web.json_response(data={
            'available_resources': registred_urls
        })
