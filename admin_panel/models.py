from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


class Protocol(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'протокол'
        verbose_name_plural = 'протоколы'

        
class Proxy(models.Model):
    info = models.TextField(default='', verbose_name='информация')
    protocol = models.ForeignKey(to=Protocol, on_delete=models.CASCADE, verbose_name='протокол')
    host = models.CharField(max_length=50, verbose_name='хост')
    port = models.SmallIntegerField(verbose_name='порт')

    ip = models.CharField(max_length=256, null=True, blank=True, verbose_name='сервер')

    username = models.CharField(max_length=256, null=True, blank=True, verbose_name='логин прокси')
    password = models.CharField(max_length=256, null=True, blank=True, verbose_name='пароль прокси')

    is_available = models.BooleanField(default=False, verbose_name='доступна?')
    response = models.CharField(max_length=32, null=True, blank=True, verbose_name='IP из ответа')

    modem_username = models.CharField(max_length=256, null=True, blank=True, verbose_name='логин модема')
    modem_password = models.CharField(max_length=256, null=True, blank=True, verbose_name='пароль модема')

    last_ip_change_time = models.DateTimeField(default=datetime.now, verbose_name='последнее изменение айпи')
    ip_change_interval = models.SmallIntegerField(default=0, verbose_name='интервал смены айпи')
    reconnect_mode = models.CharField(max_length=256, null=True, blank=True, verbose_name='режим переключения')
    owner = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='владелец')

    monitoring = models.BooleanField(default=True, verbose_name="мониторинг")
    class Meta:
        verbose_name = 'прокси'
        verbose_name_plural = 'прокси'


class Settings(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    value = models.TextField()
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'параметр'
        verbose_name_plural = 'настройки'
