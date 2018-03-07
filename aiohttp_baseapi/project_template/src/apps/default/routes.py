from core.dispatcher import SmartUrlDispatcher

from apps.default.views import DefaultView

urls = SmartUrlDispatcher()

urls.add_route('GET', r'/', DefaultView, name='default')
