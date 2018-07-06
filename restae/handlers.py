""" import modules """
import json
import traceback

import webapp2
import logging

from exceptions import NotFound, NotAuthorized, Forbidden, MissingParameter, BadRequest, MissingBody
from response import CorsResponse, JsonResponse
from helpers import get_object_from_urlsafe, get_middlewares, cached_property, get_key_from_urlsafe
from restae.exceptions import DispatchError


class BaseHandler(webapp2.RequestHandler):
    """
    BaseHandler with some intelligence & automation
    """
    model = None
    lookup_field = None
    query_param = None

    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.route_args = {}
        self.user = None

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def post(self, *args, **kwargs):
        raise NotImplementedError

    def head(self, *args, **kwargs):
        raise NotImplementedError

    def options(self, *args, **kwargs):
        raise NotImplementedError

    def put(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError

    def trace(self, *args, **kwargs):
        raise NotImplementedError

    @cached_property
    def middlewares(self):
        return get_middlewares()

    def dispatch(self):
        try:
            for middleware in self.middlewares:
                middleware.process_request(self.request)

            self.route_args = self.get_route_args()
            response = super(BaseHandler, self).dispatch()

            for middleware in self.middlewares:
                middleware.process_response(self.request, response)

            return response
        except NotFound as nf:
            return JsonResponse(status=404, data=str(nf) or 'Not found')
        except NotAuthorized as na:
            return JsonResponse(status=403, data=str(na) or 'Not authorized')
        except Forbidden as fo:
            return JsonResponse(status=401, data=str(fo) or 'Forbidden')
        except MissingParameter as mp:
            return JsonResponse(status=400, data=str(mp) or 'Missing parameter')
        except BadRequest as br:
            return JsonResponse(status=400, data=str(br) or 'Bad request')
        except MissingBody as mb:
            return JsonResponse(status=400, data=str(mb) or 'Request is missing a body')
        except ValueError as ve:
            return JsonResponse(status=400, data=str(ve) or 'Value error')

    def get_body(self):
        if self.request.body:
            try:
                json_body = json.loads(self.request.body)
                return json_body
            except Exception as err:
                logging.warning('Request is missing a body: %s -> %s',
                                err.__class__.__name__, str(err))
        raise MissingBody('Request is missing a body')

    def get_route_args(self):
        return self.request.route.regex.search(self.request.upath_info).groupdict()

    def get_object(self, urlsafe=None, query_param=None, lookup_field=None, raise_exception=True):
        _object = None
        _lookup_field = lookup_field or self.lookup_field
        _query_param = query_param or self.query_param

        if _lookup_field is None and urlsafe is None and _query_param is None:
            if raise_exception is True:
                raise BadRequest
            else:
                return None

        try:
            if urlsafe is None:
                if _lookup_field is not None and _lookup_field in self.route_args:
                    urlsafe_from_request = self.route_args[_lookup_field]
                elif _query_param is not None:
                    urlsafe_from_request = self.request.GET.get(_query_param, None)
                else:
                    urlsafe_from_request = None

                if urlsafe_from_request is None and raise_exception is False:
                    return None

                if urlsafe_from_request is None:
                    raise MissingParameter('Parameter {} is missing from request'.format(
                        _lookup_field or _query_param
                    ))
                else:
                    urlsafe = urlsafe_from_request

            _object = get_object_from_urlsafe(urlsafe)
            if not _object.check_object_permissions(self.user):
                raise NotAuthorized
        except Exception as err:
            logging.error('Error in get_object: %s -> %s\n%s',
                          err.__class__.__name__,
                          str(err),
                          traceback.format_exc())
            if raise_exception:
                raise NotFound
        finally:
            return _object


class APIHandler(BaseHandler):
    def options(self, *args, **kwargs):
        return CorsResponse()


class APIModelHandler(APIHandler):
    model = None
    queryset = None
    serializer_class = None
    
    def list(self, request, **kwargs):
        return JsonResponse(data=self.serializer_class(self.queryset, many=True).data)

    def create(self, request, **kwargs):
        obj = self.model(**self.serializer_class(data=self.get_body()).data)
        obj.put()
        return JsonResponse(data=self.serializer_class(obj).data)

    def retrieve(self, request, key=None):
        try:
            obj = key.get()
            if obj is None:
                raise NotFound
        except Exception:
            raise NotFound

        return JsonResponse(self.serializer_class(obj).data)

    def update(self, request, key=None):
        raise NotImplementedError

    def partial_update(self, request, key=None):
        raise NotImplementedError

    def destroy(self, request, key=None):
        key.delete()
        return JsonResponse()

    def dispatch(self):
        """
        Dispatches the request.

        This will first check if there's a handler_method defined in the
        matched route, and if not it'll use the method correspondent to the
        request method (``get()``, ``post()`` etc).
        """
        route_args = self.get_route_args()
        route_kwargs = {}

        has_target = 'urlsafe' in route_args

        if has_target:
            try:
                route_kwargs['key'] = get_key_from_urlsafe(route_args['urlsafe'])
            except Exception:
                return JsonResponse(status=400, data='Given urlsafe is invalid')

            if self.request.method == 'GET':
                method_name = 'retrieve'
            elif self.request.method == 'POST':
                method_name = 'update'
            elif self.request.method == 'PUT':
                method_name = 'update'
            elif self.request.method == 'DELETE':
                method_name = 'destroy'
            else:
                raise DispatchError('Invalid method / arguments')
        else:
            if self.request.method == 'GET':
                method_name = 'list'
            elif self.request.method == 'POST':
                method_name = 'create'
            else:
                raise DispatchError('Invalid method / arguments')

        method = getattr(self, method_name, None)
        # The handler only receives *args if no named variables are set.
        args, kwargs = route_args, route_kwargs
        if kwargs:
            args = ()

        try:
            return method(self, *args, **kwargs)
        except Exception, e:
            return self.handle_exception(e, self.app.debug)





