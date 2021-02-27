from django.apps import AppConfig


class ParseappConfig(AppConfig):
    name = 'parseapp'

    def ready(self):
        from SeleniumUpdater import UPDATE_parser
        UPDATE_parser.start()