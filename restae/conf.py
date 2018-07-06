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


RESTAE_SETTINGS = {
    'MIDDLEWARE_CLASSES': (
        ''
    )
}