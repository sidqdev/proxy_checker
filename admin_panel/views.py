from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from .models import Proxy
from . import funtions
from datetime import datetime
from uuid import uuid4
import json


def get_ip_address(request):
    print(request.headers)
    user_ip_address = request.headers.get('HTTP_X_FORWARDED_FOR')
    if user_ip_address:
        ip = user_ip_address.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


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


def get_hard_ip(request: HttpRequest):
    byte_count = int(request.GET.get('bytes', 32))
    cnt = byte_count // 32 + 1
    trash = ''.join([uuid4().hex for _ in range(cnt)])
    ip = get_ip_address(request)
    return HttpResponse(json.dumps(dict(query=ip, trash=trash)))
    