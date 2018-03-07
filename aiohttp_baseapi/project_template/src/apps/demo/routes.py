from core.dispatcher import SmartUrlDispatcher
from apps.demo.views import BooksListView, BookByIdView
from apps.demo.views import AuthorsListView, AuthorByIdView


urls = SmartUrlDispatcher()

urls.add_route('GET', r'/books', BooksListView, name='books-list')
urls.add_route('POST', r'/books', BooksListView, name='book-create')
urls.add_route('GET', r'/books/{id:\d+}', BookByIdView, name='book-details')
urls.add_route('PUT', r'/books/{id:\d+}', BookByIdView, name='book-update')
urls.add_route('DELETE', r'/books/{id:\d+}', BookByIdView, name='book-delete')

urls.add_route('GET', r'/authors', AuthorsListView, name='authors-list')
urls.add_route('POST', r'/authors', AuthorsListView, name='author-create')
urls.add_route('GET', r'/authors/{id:\d+}', AuthorByIdView, name='author-details')
urls.add_route('PUT', r'/authors/{id:\d+}', AuthorByIdView, name='author-update')
urls.add_route('DELETE', r'/authors/{id:\d+}', AuthorByIdView, name='author-delete')
