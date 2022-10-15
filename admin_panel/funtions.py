import os
import time

from .models import Proxy
from requests.auth import HTTPProxyAuth
from .huaweisms.api import user as api_user
from .huaweisms.api import dialup



def change_proxy_ip(proxy: Proxy):
    proxy = f'{proxy.protocol}://{proxy.host}:{proxy.port}'

    proxy = {
        'http': proxy,
        'https': proxy
    }

    auth = None
    if proxy.username:
        auth = HTTPProxyAuth(proxy.username, proxy.password)
    
    proxies_config = {'proxies': proxy, 'auth': auth}
    ctx = api_user.quick_login(os.getenv('modem_login'), os.getenv('modem_password'), modem_host="192.168.8.1", proxies_config=proxies_config)
    dialup.disconnect_mobile(ctx)
    time.sleep(20)
    dialup.connect_mobile(ctx)