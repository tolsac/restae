"""
Custom responses
"""
import six
import collections

import webob
import json


class CorsResponse(webob.Response):
    def __init__(self, *args, **kwargs):
        super(CorsResponse, self).__init__(*args, **kwargs)
        self.headers['Access-Control-Allow-Origin'] = '*'
        self.headers['Access-Control-Allow-Headers'] = ', '.join([
            'Authorization',
            'Access-Control-Allow-Headers',
            'Origin',
            'Accept',
            'X-Requested-With',
            'Content-Type',
            'Access-Control-Request-Method',
            'Access-Control-Request-Headers'
        ])
        self.headers['Access-Control-Allow-Methods'] = ', '.join([
            'POST', 'GET', 'PUT', 'DELETE'
        ])


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
        else:
            self.body = data
