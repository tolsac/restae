"""
Custom responses
"""
import six
import collections

import webob
import json

from restae.conf import settings


class CorsResponse(webob.Response):
    def __init__(self, *args, **kwargs):
        super(CorsResponse, self).__init__(*args, **kwargs)
        self.headers['Access-Control-Allow-Origin'] = ', '.join(settings.get('CORS_ALLOW_ORIGIN'))
        self.headers['Access-Control-Allow-Headers'] = ', '.join(settings.get('CORS_ALLOW_HEADERS'))
        self.headers['Access-Control-Allow-Methods'] = ', '.join(settings.get('CORS_ALLOW_METHODS'))


class JsonResponse(CorsResponse):
    def __init__(self, *args, **kwargs):
        data = None

        if 'data' in kwargs:
            data = kwargs.pop('data')
        super(JsonResponse, self).__init__(*args, **kwargs)
        self.headers['Content-type'] = 'application/json'

        if isinstance(data, (collections.Mapping, list, set, tuple)):
            self.body = json.dumps(data)
        elif isinstance(data, six.string_types):
            self.body = json.dumps({
                'message': data
            })
        elif data is not None:
            self.body = data
