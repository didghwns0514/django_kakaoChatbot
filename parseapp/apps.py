from django.apps import AppConfig


class ParseappConfig(AppConfig):
    name = 'parseapp'

    def ready(self):
        from BusinessLogic import BL_Scheduler
        BL_Scheduler.start()