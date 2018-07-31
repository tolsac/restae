"""
Exceptions classes
"""


class NotFound(Exception):
    pass


class NotAuthorized(Exception):
    pass


class Forbidden(Exception):
    pass


class MissingParameter(Exception):
    pass


class BadRequest(Exception):
    pass


class MissingBody(Exception):
    pass


class ValidationError(Exception):
    pass


class SerializerError(Exception):
    pass


class DispatchError(Exception):
    pass


class InvalidPage(Exception):
    pass