from django.contrib import admin
from .models import *
from . import scheduler
from .funtions import change_proxy_ip, reboot_modem
from threading import Thread
import time
from datetime import datetime


def reconnect_many(modeladmin, request, queryset):
    for proxy in queryset:
        proxy: Proxy
        proxy.last_ip_change_time = datetime.now()
        proxy.save()
        Thread(target=change_proxy_ip, args=(proxy,)).start()
        time.sleep(0.01)

reconnect_many.short_description = 'Переподключить'

def reboot_many(modeladmin, request, queryset):
    for proxy in queryset:
        Thread(target=reboot_modem, args=(proxy,)).start()
        time.sleep(0.01)


reboot_many.short_description = 'Перезагрузить'


class ProxyAdmin(admin.ModelAdmin):
    list_display = ('protocol', 'host', 'port', 'is_available', 'response', 'ip_change_interval', 'reconnect_mode')
    actions = (reconnect_many, reboot_many)

class SettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'value', 'description')

    def save_model(self, request, obj: Settings, form, change) -> None:
        if obj.id == 'checking_interval':
            scheduler.job.reschedule('interval', seconds=int(obj.value))
        return super().save_model(request, obj, form, change)


admin.site.register(Protocol)
admin.site.register(Proxy, ProxyAdmin)
admin.site.register(Settings, SettingAdmin)
# Register your models here.
