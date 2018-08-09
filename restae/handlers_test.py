"""
Handlers test
"""
import unittest
import sys
import webapp2
import webtest
import json

import dev_appserver
from webob import Response
from webtest import AppError

from restae.decorators import action
from restae.response import JsonResponse

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


class DynamicUserHandler(APIModelHandler):
    queryset = UserModel.query()
    serializer_class = UserModelSerializer

    @action(methods=['GET'], detail=False)
    def toto(self, *args, **kwargs):
        return Response(body='toto')

    @action(methods=['GET'], detail=True)
    def tata(self, request, key):
        return Response(body=key.get().email)


class DynamicAPIModelHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        ndb.get_context().clear_cache()

        router = Router()
        router.register('user', DynamicUserHandler)
        app = webapp2.WSGIApplication(router.urls)
        self.testapp = webtest.TestApp(app)
        self.entity = UserModel(
            email='admin@restae.com',
            first_name='admin',
            last_name='restae',
            age=28
        )
        self.entity.put()

    def test_dispatch_toto(self):
        response = self.testapp.get('/user/toto')
        self.assertEquals(response.body, 'toto')

    def test_dispatch_toto_bad_method(self):
        response = self.testapp.put('/user/toto', expect_errors=True)
        self.assertEquals(response.status_code, 404)

    def test_dispatch_toto_slash(self):
        response = self.testapp.get('/user/toto/')
        self.assertEquals(response.body, 'toto')

    def test_dispatch_tata(self):
        response = self.testapp.get('/user/{}/tata'.format(self.entity.key.urlsafe()))
        self.assertEquals(response.body, 'admin@restae.com')

    def test_dispatch_tata_with_slash(self):
        response = self.testapp.get('/user/{}/tata/'.format(self.entity.key.urlsafe()))
        self.assertEquals(response.body, 'admin@restae.com')

    def test_dispatch_tata_bad_method(self):
        response = self.testapp.post('/user/{}/tata'.format(self.entity.key.urlsafe()), expect_errors=True)
        self.assertEquals(response.status_code, 404)


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

        self.testapp.patch_json('/user/{}/'.format(self.entity.key.urlsafe()), {})
        mock_update.assert_called_once()

    @patch('restae.handlers.APIModelHandler.update', return_value=Response())
    def test_dispatch_update(self, mock_update):
        self.testapp.put_json('/user/{}/'.format(self.entity.key.urlsafe()), {})
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


class APIModelHandlerFilterTestCase(unittest.TestCase):
    def setUp(self):
        class Author(ndb.Model):
            name = ndb.StringProperty()
            lang = ndb.StringProperty()

        class AuthorSerializer(UserModelSerializer):
            class Meta:
                model = Author
                fields = '__all__'

        class Book(ndb.Model):
            name = ndb.StringProperty()
            author = ndb.KeyProperty(Author)
            page_count = ndb.IntegerProperty()

        class BookSerializer(UserModelSerializer):
            class Meta:
                model = Book
                fields = '__all__'

        class BookModelHandler(APIModelHandler):
            queryset = Book.query()
            serializer_class = BookSerializer

        class AuthorModelHandler(APIModelHandler):
            queryset = Author.query()
            serializer_class = AuthorSerializer

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        ndb.get_context().clear_cache()

        router = Router()
        router.register('book', BookModelHandler)
        router.register('author', AuthorModelHandler)

        app = webapp2.WSGIApplication(router.urls)
        self.testapp = webtest.TestApp(app)

        self.author_1 = Author(
            name='Azomov',
            lang='US'
        )
        self.author_1.put()
        self.author_2 = Author(
            name='Barjavel',
            lang='FR'
        )
        self.author_2.put()

        self.book_1 = Book(
            name='Fondation',
            page_count=1337,
            author=self.author_1.key
        )
        self.book_1.put()

        self.book_2 = Book(
            name='Ravages',
            page_count=250,
            author=self.author_2.key
        )
        self.book_2.put()

    def test_key_filter_backend(self):
        response = self.testapp.get('/book/?author={}'.format(
            self.author_1.key.urlsafe()
        ))
        json_response = json.loads(response.body)
        self.assertDictEqual(
            json_response,
            {
                u'count': 1,
                u'next': None,
                u'results': [
                    {
                        u'name': u'Fondation',
                        u'page_count': 1337,
                        u'author': self.author_1.key.urlsafe(),
                        u'key': self.book_1.key.urlsafe()
                    }
                ]
            }
        )

    def test_key_filter_backend_no_results(self):
        response = self.testapp.get('/book/?author={}'.format(
            self.book_1.key.urlsafe()
        ))
        json_response = json.loads(response.body)
        self.assertDictEqual(
            json_response,
            {
                u'count': 0,
                u'next': None,
                u'results': []
            }
        )

    def test_key_filter_backend_invalid_filter(self):
        response = self.testapp.get('/book/?toto={}'.format(
            42
        ))
        json_response = json.loads(response.body)

        self.assertDictEqual(
            json_response,
            {
                u'count': 2,
                u'next': None,
                u'results': [
                    {
                        u'page_count': 1337,
                        u'name': u'Fondation',
                        u'key': u'agx0ZXN0YmVkLXRlc3RyCgsSBEJvb2sYAww',
                        u'author': u'agx0ZXN0YmVkLXRlc3RyDAsSBkF1dGhvchgBDA'
                    },
                    {
                        u'page_count': 250,
                        u'name': u'Ravages',
                        u'key': u'agx0ZXN0YmVkLXRlc3RyCgsSBEJvb2sYBAw',
                        u'author': u'agx0ZXN0YmVkLXRlc3RyDAsSBkF1dGhvchgCDA'}
                ]
            }
        )

    def test_key_filter_backend_multiple_filter(self):
        response = self.testapp.get('/book/?page_count=1337&author={}'.format(
            self.author_1.key.urlsafe()
        ))
        json_response = json.loads(response.body)

        self.assertDictEqual(
            json_response,
            {
                u'count': 1,
                u'next': None,
                u'results': [
                    {
                        u'name': u'Fondation',
                        u'page_count': 1337,
                        u'author': self.author_1.key.urlsafe(),
                        u'key': self.book_1.key.urlsafe()
                    }
                ]
            }
        )



if __name__ == '__main__':
    unittest.main()
