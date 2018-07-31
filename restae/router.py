"""
Router
"""
from restae.handlers import APIModelHandler


class Router(object):
    """

    """
    def __init__(self):
        self.urls = []

    def get_urls_api_model(self, handler_name, handler_class):
        """
        Generates route for handler
        """
        return [
            (r'/{}/(?P<urlsafe>[^/]+)/'.format(handler_name), handler_class),
            (r'/{}/(?P<urlsafe>[^/]+)'.format(handler_name), handler_class),
            (r'/{}/'.format(handler_name), handler_class),
            (r'/{}'.format(handler_name), handler_class)
        ]

    def register(self, handler_name, handler_class):
        """
        Add handler urls to router
        """
        self.urls.extend(self.get_urls_api_model(handler_name, handler_class))
