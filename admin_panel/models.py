from django.db import models


class Protocol(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    title = models.CharField(max_length=30)


class Proxy(models.Model):
    info = models.TextField(default='')
    protocol = models.ForeignKey(to=Protocol, on_delete=models.CASCADE)
    host = models.CharField(max_length=50)
    port = models.SmallIntegerField()

    username = models.CharField(max_length=256, null=True, blank=True)
    password = models.CharField(max_length=256, null=True, blank=True)

    is_available = models.BooleanField(default=False)


class Settings(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    value = models.TextField()
    description = models.TextField(null=True, blank=True)