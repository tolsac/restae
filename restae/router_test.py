"""
Serializers test
"""
import unittest
import sys

import dev_appserver

from restae.decorators import action
from restae.response import JsonResponse

sys.path = dev_appserver.EXTRA_PATHS + sys.path


from restae.router import Router
from restae.handlers import APIHandler, APIModelHandler


class Handler(APIHandler):
    pass


class ModelHandler(APIModelHandler):
    pass


class DynamicModelHandler(APIModelHandler):
    @action(methods=['GET'], detail=False)
    def toto(self, *args, **kwargs):
        return JsonResponse(data={'ok': 42})


class BaseTestCase(unittest.TestCase):
    def test_dynamic_route(self):
        router = Router()
        handler_name = 'handler'
        router.register(handler_name, DynamicModelHandler)

        self.assertItemsEqual(
            [
                ('^/{}/$'.format(handler_name), DynamicModelHandler),
                ('^/{}$'.format(handler_name), DynamicModelHandler),
                ('^/{}/toto/$'.format(handler_name), DynamicModelHandler),
                ('^/{}/toto$'.format(handler_name), DynamicModelHandler),
                ('^/{}/(?P<urlsafe>[^/.]+)/$'.format(handler_name), DynamicModelHandler),
                ('^/{}/(?P<urlsafe>[^/.]+)$'.format(handler_name), DynamicModelHandler)
            ],
            router.urls
        )

    def test_basic_router(self):
        router = Router()
        handler_name = 'handler'
        router.register(handler_name, Handler)

        self.assertItemsEqual(
            [
                ('^/{}$'.format(handler_name), Handler),
                ('^/{}/$'.format(handler_name), Handler),
                ('^/{}/(?P<urlsafe>[^/.]+)$'.format(handler_name), Handler),
                ('^/{}/(?P<urlsafe>[^/.]+)/$'.format(handler_name), Handler)
            ],
            router.urls
        )

    def test_model_router(self):
        router = Router()
        handler_name = 'handler'
        router.register(handler_name, ModelHandler)

        self.assertItemsEqual(
            [
                ('^/{}/$'.format(handler_name), ModelHandler),
                ('^/{}$'.format(handler_name), ModelHandler),
                ('^/{}/(?P<urlsafe>[^/.]+)/$'.format(handler_name), ModelHandler),
                ('^/{}/(?P<urlsafe>[^/.]+)$'.format(handler_name), ModelHandler)
            ],
            router.urls
        )


if __name__ == '__main__':
    unittest.main()
