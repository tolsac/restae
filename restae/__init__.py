import webapp2

# Fix to allow the use of PATCH command with webapp2 base framework
webapp2.WSGIApplication.allowed_methods = webapp2.WSGIApplication.allowed_methods.union(('PATCH',))

__version__ = '1.1'
