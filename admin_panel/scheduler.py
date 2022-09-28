from apscheduler.schedulers.background import BackgroundScheduler
from .models import Proxy, Settings
import requests
from telebot import TeleBot
import os


def send_notification(proxy: Proxy):
    bot_token = Settings.objects.get(id='bot_token').value
    chat_id = int(Settings.objects.get(id='chat_id').value)

    message = f'Умерли {proxy.host}:{proxy.port}\n{proxy.info}'
    try:
        TeleBot(bot_token).send_message(chat_id, message)
    except Exception as e:
        print(e)

def is_available_proxy(protocol: str, host: str, port: int, username: str = None, password : str = None) -> bool:
    if username:
        proxy = f'{protocol}://{username}:{password}@{host}:{port}'
    else:
        proxy = f'{protocol}://{host}:{port}'

    proxy = {
        'http': proxy,
        'https': proxy
    }

    url = Settings.objects.get(id='check_url').value


    try:
        resp = requests.get(url, proxies=proxy, timeout=5)
        print(resp.status_code, host, resp.text)
        if resp.status_code == 200:
            return True
    except Exception as e:
        print(e)

    return False

    
def check():
    proxies = Proxy.objects.all()
    for proxy in proxies:
        if not is_available_proxy(proxy.protocol.id, proxy.host, proxy.port, proxy.username, proxy.password):
            if proxy.is_available:
                send_notification(proxy)
            proxy.is_available = False
            proxy.save(force_update=True)
        else:
            proxy.is_available = True
            proxy.save(force_update=True)

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
