import os
import time
import requests
from requests.auth import HTTPProxyAuth

from threading import Thread

from apscheduler.schedulers.background import BackgroundScheduler
from telebot import TeleBot

from .models import Proxy, Settings

import json

from .huaweisms.api import user as api_user
from .huaweisms.api import device

from datetime import datetime, timedelta
from .funtions import change_proxy_ip
import pytz
utc=pytz.UTC



def send_notification(proxy: Proxy, info=None, is_available=False, ip=''):
    bot_token = Settings.objects.get(id='bot_token').value
    chat_id = int(Settings.objects.get(id='chat_id').value)

    if is_available:
        message = f'{proxy.info} proxy is up\n{ip}\n{proxy.host}:{proxy.port}\n{info if info else ""}'
    else:
        message = f'{proxy.info} proxy is down\n{proxy.host}:{proxy.port}\n{info if info else ""}'

    try:
        TeleBot(bot_token).send_message(chat_id, message)
    except Exception as e:
        print(e)

def is_available_proxy(protocol: str, host: str, port: int, username: str = None, password : str = None) -> bool:
    # if username:
    #     proxy = f'{protocol}://{username}:{password}@{host}:{port}'
    # else:
    e = None
    proxy = f'{protocol}://{host}:{port}'

    proxy = {
        'http': proxy,
        'https': proxy
    }

    auth = None
    if username:
        auth = HTTPProxyAuth(username, password)

    url = Settings.objects.get(id='check_url').value

    err = 'Bad status code'
    for _ in range(int(Settings.objects.get(id='recheck_count').value)):
        try:
            resp = requests.get(url, proxies=proxy, auth=auth, timeout=int(Settings.objects.get(id='timeout').value))
            print(resp.status_code, host, resp.text)
            if resp.status_code == 200:
                if resp.text.count('.') == 3:
                    ip = json.loads(resp.text).get('query')
                    return True, None, ip
                else:
                    err = 'Incorrect response'
        except Exception as e:
            err = ' '.join(list(map(str, e.args)))

        time.sleep(int(Settings.objects.get(id='recheck_sleep').value))
    try:
        proxies_config = {'proxies': proxy, 'auth': auth}
        ctx = api_user.quick_login(os.getenv('modem_login'), os.getenv('modem_password'), modem_host="192.168.8.1", proxies_config=proxies_config)
        device.reboot(ctx)
        time.sleep(80)
    except Exception as e:
        print('reboot', e)
        err = 'Cannot connect to modem to reboot'
        return False, err, ''

    try:
        resp = requests.get(url, proxies=proxy, auth=auth, timeout=int(Settings.objects.get(id='timeout').value))
        print(resp.status_code, host, resp.text)
        if resp.status_code == 200:
            if resp.text.count('.') == 3:
                ip = json.loads(resp.text).get('query')
                return True, None, ip
            else:
                err = 'Incorrect response'
    except Exception as e:
        err = ' '.join(list(map(str, e.args)))

    return False, err, ''


def check_proxy(proxy: Proxy):
    is_available, error, resp = is_available_proxy(proxy.protocol.id, proxy.host, proxy.port, proxy.username, proxy.password)
    print(is_available, error, resp)
    if not is_available:
        if proxy.is_available:
            send_notification(proxy, error)
    
        proxy_for_update = Proxy.objects.get(id=proxy.id)
        proxy_for_update.is_available = False
        proxy_for_update.response = ''
        proxy_for_update.save()
    else:
        if not proxy.is_available:
            send_notification(proxy, is_available=True, ip=resp)
        
        proxy_for_update = Proxy.objects.get(id=proxy.id)
        proxy_for_update.is_available = True
        proxy_for_update.response = resp
        proxy_for_update.save(force_update=True)

def check():
    proxies = Proxy.objects.all()
    for proxy in proxies:
        Thread(target=check_proxy, args=(proxy,)).start()
        time.sleep(0.05)

def change_proxies_ip():
    proxies = Proxy.objects.all()
    for proxy in proxies:
        if proxy.ip_change_interval == 0:
            continue
            
        if utc.localize(proxy.last_ip_change_time + timedelta(seconds=proxy.ip_change_interval)) < datetime.now():
            continue
        
        proxy.last_ip_change_time = datetime.now()
        proxy.save()

        Thread(target=change_proxy_ip, args=(proxy,)).start()


scheduler = BackgroundScheduler()

job = None


if os.environ.get('status') == 'ok':
    sec = 120
    try:
        sec = Settings.objects.get(id='checking_interval').value
    except:
        pass
    job = scheduler.add_job(check, 'interval', seconds=int(sec))
    scheduler.add_job(change_proxies_ip, 'interval', seconds=10)
    scheduler.start()
else:
    os.environ.setdefault('status', 'ok')
