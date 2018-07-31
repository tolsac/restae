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
        pass

    def process_response(self, request, response):
        """
        Will be called after handler
        """
        pass
