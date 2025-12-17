from django.apps import AppConfig

class AppFsmdConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app_fsMD"

    def ready(self):
        import app_fsMD.signals  # noqa
