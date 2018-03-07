from aiohttp.web import UrlDispatcher, DynamicResource, PlainResource


class SmartUrlDispatcher(UrlDispatcher):
    def include(self, url_dispatcher):
        for resource in url_dispatcher.resources():
            self.register_resource(resource)

    def add_resource(self, path, *args, name=None):
        for resource in self._resources:
            resource_ident = self._get_resource_ident(resource)
            path_formatter = self._get_formatter_by_path(path)
            if resource_ident == path or resource_ident == path_formatter:
                return resource
        return super().add_resource(path, *args, name=name)

    def _get_resource_ident(self, resource) -> str:
        if isinstance(resource, DynamicResource):
            return resource._formatter
        if isinstance(resource, PlainResource):
            return resource._path

    def _get_formatter_by_path(self, path):
        resource = DynamicResource(path)
        return resource._formatter
