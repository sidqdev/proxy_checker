import os
import time

from .models import Proxy
from requests.auth import HTTPProxyAuth
from .huaweisms.api import user as api_user
from .huaweisms.api import dialup, device, sms



def change_proxy_ip(proxy: Proxy):
    if proxy.protocol == 'http' or not proxy.username:
        proxies = f'{proxy.protocol}://{proxy.host}:{proxy.port}'
    else:
        proxies = f'{proxy.protocol}://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}'
    proxies = {
        'http': proxies,
    }

    auth = None
    if proxy.username and proxy.protocol == 'http':
        auth = (proxy.username, proxy.password)
    
    proxies_config = {'proxies': proxies, 'auth': auth}
    
    ctx = api_user.quick_login(proxy.modem_username, proxy.modem_password, modem_host="192.168.8.1", proxies_config=proxies_config)
    modes = {
        '2g': 1,
        '3g': 2,
        '4g': 3,
        'auto': 0
    }
    reconnect_mode: str = proxy.reconnect_mode
    if not reconnect_mode:
        dialup.switch_network_mode(ctx, 1)
        print('disconnect')
        time.sleep(proxy.reconnect_timeout)
        dialup.switch_network_mode(ctx, 3)
        print('connect')
        api_user.logout(ctx)
        return

    for command in reconnect_mode.split(' -> '):
        if command.isdigit():
            time.sleep(int(command))
        else:
            mode = modes.get(command)
            if not mode:
                continue
            dialup.switch_network_mode(ctx, mode)

    api_user.logout(ctx)


def reboot_modem(proxy: Proxy):
    if proxy.protocol == 'http' or not proxy.username:
        proxies = f'{proxy.protocol}://{proxy.host}:{proxy.port}'
    else:
        proxies = f'{proxy.protocol}://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}'
    proxies = {
        'http': proxies,
    }

    auth = None
    if proxy.username and proxy.protocol == 'http':
        auth = (proxy.username, proxy.password)
    
    proxies_config = {'proxies': proxies, 'auth': auth}
    ctx = api_user.quick_login(proxy.modem_username, proxy.modem_password, modem_host="192.168.8.1", proxies_config=proxies_config)
    device.reboot(ctx)


def get_last_sms(proxy: Proxy):
    if proxy.protocol == 'http' or not proxy.username:
        proxies = f'{proxy.protocol}://{proxy.host}:{proxy.port}'
    else:
        proxies = f'{proxy.protocol}://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}'
    proxies = {
        'http': proxies,
    }

    auth = None
    if proxy.username and proxy.protocol == 'http':
        auth = (proxy.username, proxy.password)
    
    proxies_config = {'proxies': proxies, 'auth': auth}
    ctx = api_user.quick_login(proxy.modem_username, proxy.modem_password, modem_host="192.168.8.1", proxies_config=proxies_config)
    sms_ = sms.get_sms(ctx)
    if not sms_:
        return ''
    
    resp = sms_.get('response')
    if not resp:
        return ''

    msgs = resp.get('Messages')
    if not msgs:
        return ''
    
    msgs = msgs.get('Message')
    if not msgs:
        return ''
    
    msg = msgs[0]

    return f"Date: {msg.get('Date')}\nContent: {msg.get('Content')}"
    