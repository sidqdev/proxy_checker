from django.db import models


class Protocol(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'протокол'
        verbose_name_plural = 'протоколы'

        
class Proxy(models.Model):
    info = models.TextField(default='')
    protocol = models.ForeignKey(to=Protocol, on_delete=models.CASCADE)
    host = models.CharField(max_length=50)
    port = models.SmallIntegerField()

    username = models.CharField(max_length=256, null=True, blank=True)
    password = models.CharField(max_length=256, null=True, blank=True)

    is_available = models.BooleanField(default=False)

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
