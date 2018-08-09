"""
Restae settings file
"""


class Settings(dict):
    """
    Settings class dict-like
    """
    def override(self, _settings):
        """
        Override basic settings
        """
        self.update(_settings)


DEFAULT_PAGE_SIZE = 20
DEFAULT_PAGINATION_CLASS = 'restae.pagination.CursorPagination'

RESTAE_SETTINGS = {
    'MIDDLEWARE_CLASSES': (
        ''
    ),
    'PAGINATION_CLASS': 'restae.pagination.CursorPagination',
    'PAGE_SIZE': DEFAULT_PAGE_SIZE,

    'CORS_ALLOW_METHODS': [
       'POST', 'GET', 'PUT', 'PATCH', 'DELETE'
    ],
    'CORS_ALLOW_HEADERS': [
        'Authorization',
        'Access-Control-Allow-Headers',
        'Origin',
        'Accept',
        'X-Requested-With',
        'Content-Type',
        'Access-Control-Request-Method',
        'Access-Control-Request-Headers'
    ],
    'CORS_ALLOW_ORIGIN': ['*']
}

settings = Settings()
settings.override(RESTAE_SETTINGS)
