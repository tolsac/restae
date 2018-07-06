"""
Base middleware class
"""


class Middleware(object):
    """
    Base middleware class
    """
    def process_request(self, request):
        """
        Will be called before handler
        """
        raise NotImplementedError

    def process_response(self, request, response):
        """
        Will be called after handler
        """
        raise NotImplementedError
