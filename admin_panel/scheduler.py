import os
import time
import requests
import requests.auth

from threading import Thread

from apscheduler.schedulers.background import BackgroundScheduler
from telebot import TeleBot

from .models import Proxy, Settings


class HTTPProxyDigestAuth(requests.auth.HTTPDigestAuth):
    def handle_407(self, r):
        """Takes the given response and tries digest-auth, if needed."""

        num_407_calls = r.request.hooks['response'].count(self.handle_407)

        s_auth = r.headers.get('Proxy-authenticate', '')

        if 'digest' in s_auth.lower() and num_407_calls < 2:

            self.chal = requests.auth.parse_dict_header(s_auth.replace('Digest ', ''))

            # Consume content and release the original connection
            # to allow our new request to reuse the same one.
            r.content
            r.raw.release_conn()

            r.request.headers['Authorization'] = self.build_digest_header(r.request.method, r.request.url)
            r.request.send(anyway=True)
            _r = r.request.response
            _r.history.append(r)

            return _r

        return r

    def __call__(self, r):
        if self.last_nonce:
            r.headers['Proxy-Authorization'] = self.build_digest_header(r.method, r.url)
        r.register_hook('response', self.handle_407)
        return r


def send_notification(proxy: Proxy):
    bot_token = Settings.objects.get(id='bot_token').value
    chat_id = int(Settings.objects.get(id='chat_id').value)

    message = f'proxy is down {proxy.info}\n{proxy.host}:{proxy.port}'
    try:
        TeleBot(bot_token).send_message(chat_id, message)
    except Exception as e:
        print(e)

def is_available_proxy(protocol: str, host: str, port: int, username: str = None, password : str = None) -> bool:
    # if username:
    #     proxy = f'{protocol}://{username}:{password}@{host}:{port}'
    # else:
    proxy = f'{protocol}://{host}:{port}'

    proxy = {
        'http': proxy,
        'https': proxy
    }
    
    if protocol == 'https':
        proxy = {
            'https': proxy
        }
    if protocol == 'http':
        proxy = {
            'http': proxy,
        }

    auth = None
    if username:
        auth = HTTPProxyDigestAuth(username, password)
    url = Settings.objects.get(id='check_url').value

    for _ in range(int(Settings.objects.get(id='recheck_count').value)):
        try:
            resp = requests.get(url, proxies=proxy, auth=auth, timeout=5)
            print(resp.status_code, host, resp.text)
            if resp.status_code == 200:
                return True
        except Exception as e:
            print(e)

        time.sleep(int(Settings.objects.get(id='recheck_sleep').value))

    return False


def check_proxy(proxy: Proxy):
    if not is_available_proxy(proxy.protocol.id, proxy.host, proxy.port, proxy.username, proxy.password):
        if proxy.is_available:
            send_notification(proxy)
        proxy.is_available = False
        proxy.save(force_update=True)
    else:
        proxy.is_available = True
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
