from django.contrib import admin
from .models import *
from . import scheduler
from .funtions import change_proxy_ip, reboot_modem
from threading import Thread
import time
from datetime import datetime, timedelta


def ssh_update(modeladmin, request, queryset):
    for proxy in queryset:
        Thread(target=scheduler.ssh_connect, args=(proxy,)).start()
        proxy.ssh_last_execute = datetime.now()
        proxy.save()
        time.sleep(0.1)


ssh_update.short_description = 'Обновить ssh'


def monitor(modeladmin, request, queryset):
    queryset.update(monitoring=True)


monitor.short_description = 'Мониторить'


def unmonitor(modeladmin, request, queryset):
    queryset.update(monitoring=False)


unmonitor.short_description = 'Перестать мониторить'


def reconnect_many(modeladmin, request, queryset):
    for proxy in queryset:
        proxy: Proxy
        proxy.last_ip_change_time = datetime.now()
        proxy.save()
        Thread(target=change_proxy_ip, args=(proxy,)).start()
        time.sleep(0.01)

reconnect_many.short_description = 'Сменить ip'

def reboot_many(modeladmin, request, queryset):
    for proxy in queryset:
        Thread(target=reboot_modem, args=(proxy,)).start()
        time.sleep(0.01)


reboot_many.short_description = 'Перезагрузить'


class ProxyAdmin(admin.ModelAdmin):
    # list_display = ('protocol', 'host', 'port', 'is_available', 'response', 'ip_change_interval', 'reconnect_mode')
    # list_display = ('ip', 'port', 'info', 'is_available', 'response')
    actions = (reconnect_many, reboot_many, monitor, unmonitor, ssh_update)
    # list_display_links = []

    def get_queryset(self, request):
        qs = super(ProxyAdmin, self).get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(owner=request.user)

    def get_list_display_links(self, request, list_display):
        if request.user.is_superuser:
            return super(ProxyAdmin, self).get_list_display_links(request, list_display)
        return []
    
    def get_list_display(self, request):
        if request.user.is_superuser:
            return ('protocol', 'host', 'port', 'is_available', 'response', 'ip_change_interval', 'reconnect_mode', 'monitoring')

        return ('ip', 'port', 'info', 'is_available', 'response', 'monitoring')


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
