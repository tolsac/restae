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


DEFAULT_PAGE_SIZE = 5
DEFAULT_PAGINATION_CLASS = 'restae.pagination.CursorPagination'

RESTAE_SETTINGS = {
    'MIDDLEWARE_CLASSES': (
        ''
    ),
    'PAGINATION_CLASS': 'restae.pagination.CursorPagination',
    'PAGE_SIZE': DEFAULT_PAGE_SIZE
}

settings = Settings()
settings.override(RESTAE_SETTINGS)
