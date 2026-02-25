from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # The Config Registry: Necessary for nested autodiscovery
    name = 'apps.accounts' 

    def ready(self):
        """
        Task 1: App Config
        Register signals when app is ready.
        """
        import apps.accounts.signals
