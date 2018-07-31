"""
Middleware tests
"""
import unittest
import sys
import webapp2
import webtest

import dev_appserver
from webob import Response

sys.path = dev_appserver.EXTRA_PATHS + sys.path

from google.appengine.ext import testbed, ndb

from restae.handlers import APIHandler
from restae.middleware import Middleware
from restae.router import Router
from restae.conf import settings


class TestRequestMiddleware(Middleware):
    def process_request(self, request):
        request.value = 'request'


class TestResponseMiddleware(Middleware):
    def process_response(self, request, response):
        response.body = 'response'


class APIUserHandler(APIHandler):
    def get(self, *args, **kwargs):
        return Response(body=self.request.value)

    def post(self, *args, **kwargs):
        return Response()


class APIHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        ndb.get_context().clear_cache()

        router = Router()
        router.register('user', APIUserHandler)
        app = webapp2.WSGIApplication(router.urls)
        self.testapp = webtest.TestApp(app)

    def test_request_middleware(self):
        settings.override({
            'MIDDLEWARE_CLASSES': ['restae.middleware_test.TestRequestMiddleware']
        })

        response = self.testapp.get('/user/')
        self.assertEquals(response.body, 'request')

    def test_response_middleware(self):
        settings.override({
            'MIDDLEWARE_CLASSES': ['restae.middleware_test.TestResponseMiddleware']
        })

        response = self.testapp.post('/user/')
        self.assertEquals(response.body, 'response')


if __name__ == '__main__':
    unittest.main()
