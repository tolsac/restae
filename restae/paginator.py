"""
Paginator working ith datastore
"""
# from google.appengine.ext.ndb import Cursor
#
# from src.settings import RESULTS_PER_PAGE
#
#
# class Paginator(object):
#     """
#     Paginates datastore entities
#     """
#     def __init__(self, handler, **kwargs):
#         self.handler = handler
#         self.page_size = int(self.handler.request.GET.get('maxResults') or RESULTS_PER_PAGE)
#
#         self.list_params = {
#             'user': self.handler.user,
#         }
#
#         if 'query' in self.handler.request.GET:
#             self.list_params['search_text'] = self.handler.request.GET.get('query')
#
#         self.cursor = kwargs.pop('cursor', None)
#         authorized_areas = getattr(self.handler, 'authorized_areas', None)
#         if authorized_areas:
#             kwargs['authorized_areas'] = authorized_areas
#         self.model = kwargs.get('model') or self.handler.model
#         self.details = bool(self.handler.request.GET.get('details', False) or kwargs.get('details', False))
#         if 'details' in kwargs:
#             kwargs.pop('details')
#         self.list_params.update(kwargs)
#
#     def get_page(self):
#
#         query = self.model.list(**self.list_params)
#
#         if isinstance(query, (list, set, tuple)):
#             return {
#                 'items': [item.to_dict() for item in query],
#                 'totalResults': len(query),
#                 'nextPageToken': None
#             }
#
#         total_results = query.count()
#         results, next_cursor, more = query.fetch_page(
#             self.page_size, start_cursor=Cursor(urlsafe=self.cursor))
#
#         next_page_token = None
#         if more:
#             next_page_token = next_cursor.urlsafe()
#
#         if self.details:
#             serializer = lambda x: x.to_dict(details=True)
#         else:
#             serializer = lambda x: x.to_dict()
#
#         return {
#             'items': [serializer(item) for item in results],
#             'nextPageToken': next_page_token,
#             'totalResults': total_results
#         }
