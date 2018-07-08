"""
Rest helpers
"""
import importlib
import threading

from google.appengine.ext import ndb

from restae.conf import settings

KEY_CLASS = ndb.Key


class cached_property(object):
    """A decorator that converts a function into a lazy property.

    The function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::

        class Foo(object):

            @cached_property
            def foo(self):
                # calculate something important here
                return 42

    The class has to have a `__dict__` in order for this property to
    work.

    .. note:: Implementation detail: this property is implemented as non-data
       descriptor.  non-data descriptors are only invoked if there is
       no entry with the same name in the instance's __dict__.
       this allows us to completely get rid of the access function call
       overhead.  If one choses to invoke __get__ by hand the property
       will still work as expected because the lookup logic is replicated
       in __get__ for manual invocation.

    This class was ported from `Werkzeug`_ and `Flask`_.
    """

    _default_value = object()

    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func
        self.lock = threading.RLock()

    def __get__(self, obj, type=None):
        if obj is None:
            return self

        with self.lock:
            value = obj.__dict__.get(self.__name__, self._default_value)
            if value is self._default_value:
                value = self.func(obj)
                obj.__dict__[self.__name__] = value

            return value


def get_key_from_urlsafe(urlsafe):
    """
    Build a Key with given urlsafe
    """
    return ndb.Key(urlsafe=urlsafe)


def get_model_class_from_query(query):
    """
    Return model class from any query.
    Note that the model needs to be imported once
    in the application
    """
    return ndb.Model._lookup_model(query.kind)


def get_object_from_urlsafe(urlsafe):
    """
    Build a Key with given urlsafe and get the object
    """
    return get_key_from_urlsafe(urlsafe).get()


def load_class(full_class_string):
    """
    Dynamically load a class from a string
    """
    class_data = full_class_string.split('.')
    module_path = '.'.join(class_data[:-1])
    class_str = class_data[-1]

    module = importlib.import_module(module_path)
    # Finally, we retrieve the Class
    return getattr(module, class_str, None)


def get_middlewares():
    """
    Return all middleware classes
    """
    middlewares = []

    for middleware in settings.get('MIDDLEWARE_CLASSES', []):
        middlewares.append(load_class(middleware)())

    return middlewares
