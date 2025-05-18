from django.apps import AppConfig


class BaseAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base_app'
    
    def ready(self):
        """
        Run when Django loads this app to register signals and perform other initialization.
        """
        # Import the models here to avoid circular imports
        import base_app.models