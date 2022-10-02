import os
import time
import requests
from requests.auth import HTTPProxyAuth

from threading import Thread

from apscheduler.schedulers.background import BackgroundScheduler
from telebot import TeleBot

from .models import Proxy, Settings


def send_notification(proxy: Proxy, info=None, is_available=False):
    bot_token = Settings.objects.get(id='bot_token').value
    chat_id = int(Settings.objects.get(id='chat_id').value)

    msg = 'proxy is up' if is_available else 'proxy is down'
    message = f'{proxy.info} {msg}\n{proxy.host}:{proxy.port}\n\n\n{info if info else ""}'
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

    for _ in range(int(Settings.objects.get(id='recheck_count').value)):
        try:
            resp = requests.get(url, proxies=proxy, auth=auth, timeout=int(Settings.objects.get(id='timeout').value))
            print(resp.status_code, host, resp.text)
            if resp.status_code == 200:
                if resp.text.count('.') == '3':
                    return True, None, resp.text
                else:
                    return False, 'Incorrect response', ''
        except Exception as e:
            return False, ' '.join(list(map(str, e.args))), ''

        time.sleep(int(Settings.objects.get(id='recheck_sleep').value))

    return False, 'Bad status code', ''


def check_proxy(proxy: Proxy):
    is_available, error, resp = is_available_proxy(proxy.protocol.id, proxy.host, proxy.port, proxy.username, proxy.password)
    if not is_available:
        if proxy.is_available:
            send_notification(proxy, error)
        proxy.is_available = False
        proxy.response = ''
        proxy.save(force_update=True)
    else:
        if not proxy.is_available:
            send_notification(proxy, is_available=True)
        proxy.is_available = True
        proxy.response = resp
        proxy.save(force_update=True)

def check():
    proxies = Proxy.objects.all()
    for proxy in proxies:
        Thread(target=check_proxy, args=(proxy,)).start()
        time.sleep(0.05)
    

scheduler = BackgroundScheduler()

job = None


if os.environ.get('status') == 'ok':
    sec = 120
    try:
        sec = Settings.objects.get(id='checking_interval').value
    except:
        pass
    job = scheduler.add_job(check, 'interval', seconds=int(sec))
    scheduler.start()
else:
    os.environ.setdefault('status', 'ok')
