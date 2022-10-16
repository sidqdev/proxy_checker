from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from .models import Proxy
from . import funtions
from threading import Thread
from datetime import datetime

def change_proxy_ip_endpoint(request: HttpRequest):
    if request.GET.get('id'):
        id = int(request.GET.get('id'))
        proxy = Proxy.objects.get(pk=id)
    elif request.GET.get('port'):
        port = int(request.GET.get('port'))
        proxy = Proxy.objects.get(port=port)
    else:
        return HttpResponse("no args")
        
    proxy.last_ip_change_time = datetime.now()
    proxy.save()
    try:
        funtions.change_proxy_ip(proxy)
    except:
        return HttpResponse("modem not available")
    return HttpResponse("ip change success")