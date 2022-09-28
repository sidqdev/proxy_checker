from django.apps import AppConfig

class AdminPanelConfig(AppConfig):
    name = 'admin_panel'
    def ready(self):
        print('READY!!!')