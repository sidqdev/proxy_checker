import os
import time

from .models import Proxy
from requests.auth import HTTPProxyAuth
from .huaweisms.api import user as api_user
from .huaweisms.api import dialup



def change_proxy_ip(proxy: Proxy):
    proxies = f'{proxy.protocol}://{proxy.host}:{proxy.port}'

    proxies = {
        'http': proxies,
    }

    auth = None
    if proxy.username:
        auth = (proxy.username, proxy.password)
    
    proxies_config = {'proxies': proxies, 'auth': auth}
    ctx = api_user.quick_login("", "", modem_host="192.168.8.1", proxies_config=proxies_config)
    dialup.switch_network_mode(ctx, 1)
    print('disconnect')
    time.sleep(proxy.reconnect_timeout)
    dialup.switch_network_mode(ctx, 3)
    print('connect')
    api_user.logout(ctx)