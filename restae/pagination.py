"""
Paginator working with datastore
"""

from collections import OrderedDict

from google.appengine.api.datastore_errors import BadValueError
from google.appengine.ext.ndb import Cursor

from restae.response import JsonResponse
from restae.conf import settings, DEFAULT_PAGE_SIZE
from restae.exceptions import InvalidPage, NotFound, BadRequest


class BasePagination(object):
    display_page_controls = False

    def paginate_queryset(self, queryset, request, view=None):
        raise NotImplementedError('paginate_queryset() must be implemented.')

    def get_paginated_response(self, data):  # pragma: no cover
        raise NotImplementedError('get_paginated_response() must be implemented.')

    def get_results(self, data):
        return data['results']

    def get_page_size(self, request):
        return request.GET.get('page_size', settings.get('PAGE_SIZE', DEFAULT_PAGE_SIZE))


class CursorPagination(BasePagination):
    """
    A simple cursor based style that supports cursors urlsafe as
    query parameters. For example:
    http://api.example.org/accounts/?page_token=<URLSAFE STRING>
    """
    count = None
    page = None
    next_page_token = None
    has_next = None

    def get_page_token(self, request):
        return request.GET.get('page_token', None)

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """

        self.count = queryset.count()

        try:
            self.page, self.next_page_token, self.has_next = queryset.fetch_page(
                self.get_page_size(request), start_cursor=Cursor(urlsafe=self.get_page_token(request)))
        except InvalidPage:
            raise NotFound('Requested page not found')
        except BadValueError as err:
            raise BadRequest(str(err))

        return list(self.page)

    def get_paginated_response(self, data):
        return JsonResponse(data=OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

    def get_next_link(self):
        if not self.has_next:
            return None
        return self.next_page_token.urlsafe()

    def get_previous_link(self):
        return None
