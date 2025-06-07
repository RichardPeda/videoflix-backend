from django.apps import AppConfig


class MovieConfig(AppConfig):
    """
    Configure application settings for the 'movie' Django app.

    This class defines the AppConfig for the 'movie' application and allows
    custom initialization logic when the app is ready.

    Key features:
    - Sets the default primary key field type to BigAutoField for all models in the app.
    - Specifies the name of the app as 'movie'.
    - Overrides the `ready` method to import signal handlers when the app is loaded.

    Attributes:
    - default_auto_field: Sets the default auto-incrementing primary key field type.
    - name: Defines the full Python path to the app.

    Methods:
    - ready(): This method is called when the Django app registry is fully populated.
    It imports the `signals` module from the current package to ensure that any signal
    handlers are properly registered (e.g., for model lifecycle events like post_save).
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movie'
    
    def ready(self):
        from . import signals
