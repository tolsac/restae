"""
Serializers test
"""
import unittest
import sys

import dev_appserver
sys.path = dev_appserver.EXTRA_PATHS + sys.path


from restae.router import Router
from restae.handlers import APIHandler, APIModelHandler


class Handler(APIHandler):
    pass

class ModelHandler(APIModelHandler):
    pass


class BaseTestCase(unittest.TestCase):
    def test_basic_router(self):
        router = Router()
        handler_name = 'handler'
        router.register(handler_name, Handler)

        self.assertListEqual(
            [
                (r'/{}/(?P<urlsafe>[^/]+)/'.format(handler_name), Handler),
                (r'/{}/(?P<urlsafe>[^/]+)'.format(handler_name), Handler),
                (r'/{}/'.format(handler_name), Handler),
                (r'/{}'.format(handler_name), Handler)
            ],
            router.urls
        )

    def test_model_router(self):
        router = Router()
        handler_name = 'handler'
        router.register(handler_name, ModelHandler)

        self.assertListEqual(
            [
                (r'/{}/(?P<urlsafe>[^/]+)/'.format(handler_name), ModelHandler),
                (r'/{}/(?P<urlsafe>[^/]+)'.format(handler_name), ModelHandler),
                (r'/{}/'.format(handler_name), ModelHandler),
                (r'/{}'.format(handler_name), ModelHandler)
            ],
            router.urls
        )


if __name__ == '__main__':
    unittest.main()
