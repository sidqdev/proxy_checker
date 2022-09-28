from apscheduler.schedulers.background import BackgroundScheduler
from .models import Proxy, Settings
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from telebot import TeleBot
import os


def send_notification(proxy: Proxy):
    bot_token = Settings.objects.get(id='bot_token').value
    chat_id = int(Settings.objects.get(id='chat_id').value)

    message = f'proxy is down {proxy.info}\n{proxy.host}:{proxy.port}'
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
    
    if protocol == 'https':
        proxy = {
            'https': proxy
        }
    # if protocol == 'http':
    #     proxy = {
    #         'http': proxy
    #     }

    url = Settings.objects.get(id='check_url').value


    try:
        # session = requests.Session()
        # retry = Retry(connect=3, backoff_factor=0.5)
        # adapter = HTTPAdapter(max_retries=retry)
        # session.mount('http://', adapter)
        # session.mount('https://', adapter)

        # resp = session.get(url, proxies=proxy, timeout=10)

        resp = requests.get(url, proxies=proxy, timeout=15)
        print(resp.status_code, host, resp.text)
        # session.close()
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
