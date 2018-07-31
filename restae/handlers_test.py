"""
Handlers test
"""
import unittest
import sys
import webapp2
import webtest

import dev_appserver
from webob import Response
from webtest import AppError

sys.path = dev_appserver.EXTRA_PATHS + sys.path

from google.appengine.ext import testbed, ndb
from mock import patch

from restae import serializers
from restae.handlers import APIModelHandler, APIHandler
from restae.router import Router


class UserModel(ndb.Model):
    email = ndb.StringProperty()
    last_name = ndb.StringProperty()
    first_name = ndb.StringProperty()
    age = ndb.IntegerProperty()


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = UserModel


class UserHandler(APIModelHandler):
    queryset = UserModel.query()
    serializer_class = UserModelSerializer


class APIModelHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        ndb.get_context().clear_cache()

        router = Router()
        router.register('user', UserHandler)
        app = webapp2.WSGIApplication(router.urls)
        self.testapp = webtest.TestApp(app)
        self.entity = UserModel(
            email='admin@restae.com',
            first_name='admin',
            last_name='restae',
            age=28
        )
        self.entity.put()

    @patch('restae.handlers.APIModelHandler.list', return_value=Response())
    def test_dispatch_list(self, mock_list):
        self.testapp.get('/user/')
        mock_list.assert_called_once()

    @patch('restae.handlers.APIModelHandler.create', return_value=Response())
    def test_dispatch_create(self, mock_create):
        self.testapp.post_json('/user/', {})
        mock_create.assert_called_once()

    @patch('restae.handlers.APIModelHandler.partial_update', return_value=Response())
    def test_dispatch_partial_update(self, mock_update):
        with self.assertRaises(AppError):
            response = self.testapp.put_json('/user/', {})
            self.assertEquals(response.status_code, 404)

        self.testapp.put_json('/user/{}/'.format(self.entity.key.urlsafe()), {})
        mock_update.assert_called_once()

    @patch('restae.handlers.APIModelHandler.update', return_value=Response())
    def test_dispatch_update(self, mock_update):
        self.testapp.post_json('/user/{}/'.format(self.entity.key.urlsafe()), {})
        mock_update.assert_called_once()

    @patch('restae.handlers.APIModelHandler.destroy', return_value=Response())
    def test_dispatch_destroy(self, mock_destroy):
        self.testapp.delete('/user/{}/'.format(self.entity.key.urlsafe()))
        mock_destroy.assert_called_once()

    @patch('restae.handlers.APIModelHandler.retrieve', return_value=Response())
    def test_dispatch_retrieve(self, mock_retrieve):
        self.testapp.get('/user/{}/'.format(self.entity.key.urlsafe()))
        mock_retrieve.assert_called_once()


class APIUserHandler(APIHandler):
    def get(self, *args, **kwargs):
        return Response(body='get')

    def post(self, *args, **kwargs):
        return Response(body='post')

    def put(self, *args, **kwargs):
        return Response(body='put')

    def delete(self, *args, **kwargs):
        return Response(body='delete')

    def patch(self, *args, **kwargs):
        return Response(body='patch')


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

    def test_dispatch_get(self):
        response = self.testapp.get('/user/')
        self.assertEquals(response.body, 'get')

    def test_dispatch_post(self):
        response = self.testapp.post('/user/')
        self.assertEquals(response.body, 'post')

    def test_dispatch_put(self):
        response = self.testapp.put('/user/')
        self.assertEquals(response.body, 'put')

    def test_dispatch_patch(self):
        response = self.testapp.patch('/user/')
        self.assertEquals(response.body, 'patch')

    def test_dispatch_delete(self):
        response = self.testapp.delete('/user/')
        self.assertEquals(response.body, 'delete')


if __name__ == '__main__':
    unittest.main()
