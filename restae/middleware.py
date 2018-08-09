"""
Base middleware class
"""
import webapp2


class Middleware(object):
    """
    Base middleware class
    """
    ACTIVATE_ON_METHODS = webapp2.WSGIApplication.allowed_methods.union(('PATCH',))

    def activate_on_method(self, method):
        return method.upper() in self.ACTIVATE_ON_METHODS

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
