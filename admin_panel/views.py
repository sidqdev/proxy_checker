from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from .models import Proxy
from . import funtions
from threading import Thread


def change_proxy_ip_endpoint(request: HttpRequest):
    id = int(request.GET.get('id'))
    proxy = Proxy.objects.get(pk=id)
    Thread(funtions.change_proxy_ip, args=(proxy,)).start()
    return HttpResponse("in process")