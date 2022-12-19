from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
import sys

nl_bl = {'null': True, 'blank': True}


def get_default(var_id: str, data_type): 
    def getting_default():
        try:
            result = data_type(Settings.objects.get(id=var_id).value)
        except:
            result = data_type()
        return result

    if sys.argv[1] not in ['migrate', 'makemigrations']:
        return getting_default

    else: 
        return None


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

    ip = models.CharField(max_length=256, **nl_bl, verbose_name='сервер')

    username = models.CharField(default=get_default('username', str), max_length=256, **nl_bl, verbose_name='логин прокси')
    password = models.CharField(default=get_default('password', str), max_length=256, **nl_bl, verbose_name='пароль прокси')

    is_available = models.BooleanField(default=False, verbose_name='доступна?')
    response = models.CharField(max_length=32, **nl_bl, verbose_name='IP из ответа')

    modem_username = models.CharField(max_length=256, **nl_bl, verbose_name='логин модема')
    modem_password = models.CharField(max_length=256, **nl_bl, verbose_name='пароль модема')

    last_ip_change_time = models.DateTimeField(default=datetime.now, verbose_name='последнее изменение айпи')
    ip_change_interval = models.SmallIntegerField(default=0, verbose_name='интервал смены айпи')
    reconnect_mode = models.CharField(max_length=256, **nl_bl, verbose_name='режим переключения')
    owner = models.ForeignKey(to=User, on_delete=models.SET_NULL, **nl_bl, verbose_name='владелец')

    monitoring = models.BooleanField(default=True, verbose_name="мониторинг")

    ssh_host = models.CharField(max_length=50, **nl_bl, verbose_name='ssh хост')
    ssh_port = models.SmallIntegerField(default=get_default('ssh_port', int), **nl_bl, verbose_name='ssh порт')
    ssh_user = models.CharField(default=get_default('ssh_user', str), max_length=50, **nl_bl, verbose_name='ssh пользователь')
    ssh_password = models.CharField(default=get_default('ssh_password', str), max_length=50, **nl_bl, verbose_name='ssh пароль')
    ssh_command = models.CharField(default=get_default('ssh_command', str), max_length=256, **nl_bl, verbose_name='ssh команда')
    ssh_last_execute =  models.DateTimeField(default=datetime.now, verbose_name='последнее обновление ssh')
    ssh_execute_interval = models.SmallIntegerField(default=0, **nl_bl, verbose_name='интервал обновления')

    last_pay = models.DateField(default=datetime.now(), **nl_bl, verbose_name='постледняя дата оплаты')
    pay_days_interval = models.SmallIntegerField(default=30, **nl_bl, verbose_name='интервал оплаты (дни)')
    allert_interval_days = models.SmallIntegerField(default=get_default('allert_interval', int), max_length=256, **nl_bl, verbose_name='интервал оповещения (дни)')
    user_id = models.BigIntegerField(default=get_default('user_id', int), verbose_name='id пользователя')


    class Meta:
        verbose_name = 'прокси'
        verbose_name_plural = 'прокси'


class Settings(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    value = models.TextField()
    description = models.TextField(**nl_bl)


    class Meta:
        verbose_name = 'параметр'
        verbose_name_plural = 'настройки'
