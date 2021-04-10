from django.apps import AppConfig


class ParsenewsappConfig(AppConfig):
    name = 'parsenewsapp'


    def ready(self):
        from BusinessLogic import BL_Scheduler
        BL_Scheduler.start_stock()