from django.contrib import admin
from .models import *
from . import scheduler

class ProxyAdmin(admin.ModelAdmin):
    list_display = ('protocol', 'host', 'port', 'is_available')


class SettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'value', 'description', 'response')

    def save_model(self, request, obj: Settings, form, change) -> None:
        if obj.id == 'checking_interval':
            scheduler.job.reschedule('interval', seconds=int(obj.value))
        return super().save_model(request, obj, form, change)


admin.site.register(Protocol)
admin.site.register(Proxy, ProxyAdmin)
admin.site.register(Settings, SettingAdmin)
# Register your models here.
