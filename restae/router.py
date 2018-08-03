"""
Router
"""
import itertools

from restae.exceptions import ImproperlyConfigured


def escape_curly_brackets(url_path):
    """
    Double brackets in regex of url_path for escape string formatting
    """
    if ('{' and '}') in url_path:
        url_path = url_path.replace('{', '{{').replace('}', '}}')
    return url_path


class Route(object):
    """
    A route mapping representation contains the URL, METHOD and route type
    """
    def __init__(self, **kwargs):
        self.url = kwargs.pop('url')
        self.mapping = kwargs.get('mapping')
        self.detail = kwargs.pop('detail')
        self.is_dynamic = kwargs.pop('is_dynamic')


class Url(object):
    """
    An URL representation contains the Route and the destination Handler
    """
    def __init__(self, **kwargs):
        self.route = kwargs.pop('route')
        self.regex = kwargs.pop('regex')
        self.handler_class = kwargs.pop('handler_class')
        self.handler_name = kwargs.pop('handler_name')

    def copy(self):
        return Url(
            route=self.route,
            regex=self.regex,
            handler_class=self.handler_class,
            handler_name=self.handler_name
        )


class Router(object):
    """
    The default router
    """
    routes = [
        # List route.
        Route(
            url=r'^/{prefix}',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            detail=False,
            is_dynamic=False
        ),
        # Dynamically generated list routes. Generated using
        # @action(detail=False) decorator on methods of the handler.
        Route(
            url=r'^/{prefix}/{url_path}',
            detail=False,
            is_dynamic=True
        ),
        # Detail route.
        Route(
            url=r'^/{prefix}/{lookup}',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            detail=True,
            is_dynamic=False
        ),
        # Dynamically generated detail routes. Generated using
        # @action(detail=True) decorator on methods of the handler.
        Route(
            url=r'^/{prefix}/{lookup}/{url_path}',
            detail=True,
            is_dynamic=True
        ),
    ]

    def __init__(self):
        self.registry = []

    def register(self, handler_name, handler_class):
        assert handler_name is not None and handler_class is not None, (
            '\'handler_name\' and \'handler_class\' arguments are required '
            'when calling \'register\' function from router.'
        )
        self.registry.append((handler_name, handler_class))

    def get_lookup_regex(self, handler):
        """
        Given a handler, return the portion of URL regex that is used
        to match against a single instance.
        """
        base_regex = '(?P<{lookup_url_kwarg}>{lookup_value})'
        # Use `urlsafe` as default field.
        lookup_field = getattr(handler, 'lookup_field', None) or 'urlsafe'
        lookup_url_kwarg = getattr(handler, 'lookup_url_kwarg', None) or lookup_field
        lookup_value = getattr(handler, 'lookup_value_regex', '[^/.]+')
        return base_regex.format(
            lookup_url_kwarg=lookup_url_kwarg,
            lookup_value=lookup_value
        )

    def _get_dynamic_route(self, route, action):
        url_path = escape_curly_brackets(action.url_path)

        return Route(
            url=route.url.replace('{url_path}', url_path),
            mapping=action.mapping,
            detail=route.detail,
            is_dynamic=True
        )

    def get_routes(self, handler):
        """
        Augment `self.routes` with any dynamically generated routes.
        Returns a list of the Route class.
        """
        # converting to list as iterables are good for one pass, known host needs to be checked again and again for
        # different functions.
        known_actions = list(itertools.chain(*[route.mapping.values() for route in self.routes if not route.is_dynamic]))
        extra_actions = handler.get_extra_actions()

        # checking action names against the known actions list
        not_allowed = [
            action.__name__ for action in extra_actions
            if action.__name__ in known_actions
        ]
        if not_allowed:
            msg = ('Cannot use the @action decorator on the following '
                   'methods, as they are existing routes: %s')
            raise ImproperlyConfigured(msg % ', '.join(not_allowed))

        # partition detail and list actions
        detail_actions = [action for action in extra_actions if action.detail]
        list_actions = [action for action in extra_actions if not action.detail]

        routes = []
        dynamic_routes = []
        for route in self.routes:
            if route.is_dynamic and route.detail:
                dynamic_routes += [self._get_dynamic_route(route, action) for action in detail_actions]
            elif route.is_dynamic and not route.detail:
                dynamic_routes += [self._get_dynamic_route(route, action) for action in list_actions]
            else:
                routes.append(route)

        return dynamic_routes + routes

    def get_method_map(self, handler, method_map):
        """
        Given an handler, and a mapping of http methods to actions,
        return a new mapping which only includes any mappings that
        are actually implemented by the viewset.
        """
        bound_methods = {}
        for method, action in method_map.items():
            if hasattr(handler, action):
                bound_methods[method] = action
        return bound_methods

    def get_urls(self):
        """
        Use the registered handlers to generate a list of URL patterns.
        """
        urls = []

        for handler_name, handler_class in self.registry:
            lookup = self.get_lookup_regex(handler_class)
            routes = self.get_routes(handler_class)
            ret = []

            for route in routes:

                # Only actions which actually exist on the viewset will be bound
                # mapping = self.get_method_map(handler_class, route.mapping)
                # if not mapping:
                #     continue

                # Build the url pattern
                regex = route.url.format(
                    prefix=handler_name,
                    lookup=lookup,
                )

                _url_with_slash = Url(
                    handler_class=handler_class,
                    handler_name=handler_name,
                    route=route,
                    regex=regex + '/$'
                )
                _url_without_slash = Url(
                    handler_class=handler_class,
                    handler_name=handler_name,
                    route=route,
                    regex=regex + '$'
                )

                ret.append(_url_with_slash)
                ret.append(_url_without_slash)
                urls.append(_url_with_slash)
                urls.append(_url_without_slash)

            setattr(handler_class, 'urls', ret)
        return urls

    @property
    def urls(self):
        if not hasattr(self, '_urls'):
            self._urls = []

            for _url in self.get_urls():
                self._urls.append((
                    _url.regex,
                    _url.handler_class
                ))
        return self._urls
