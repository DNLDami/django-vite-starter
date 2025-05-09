from django.apps import AppConfig


class AAccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.a_account'
    
    def ready(self):
        import apps.a_account.signals
