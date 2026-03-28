from django.apps import AppConfig


class HtkappConfig(AppConfig):
    name = 'htkapp'
def ready(self):
    import htkapp.signals