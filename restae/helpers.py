"""
Rest helpers
"""
from google.appengine.ext.ndb import Key


KEY_CLASS = Key


def get_key_from_urlsafe(urlsafe):
    """
    Build a Key with given urlsafe
    """
    return Key(urlsafe=urlsafe)


def get_object_from_urlsafe(urlsafe):
    """
    Build a Key with given urlsafe and get the object
    """
    return get_key_from_urlsafe(urlsafe).get()
