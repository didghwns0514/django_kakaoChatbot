from django.apps import AppConfig


class AppstockinfoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appStockInfo'

    def ready(self):
        from scheduler import taskStockKR, taskStockUS
        taskStockKR()
        taskStockUS()
