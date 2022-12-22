import os
import time
import requests
from requests.auth import HTTPProxyAuth

from threading import Thread

from apscheduler.schedulers.background import BackgroundScheduler
from telebot import TeleBot

from .models import Proxy, Settings

import json

from datetime import date, datetime, timedelta, timezone
from .funtions import change_proxy_ip, reboot_modem, get_last_sms
import pytz
from paramiko import SSHClient, AutoAddPolicy


utc=pytz.UTC


def send_notification(proxy: Proxy, info=None, is_available=False, ip='', sms=''):
    bot_token = Settings.objects.get(id='bot_token').value
    chat_id = int(Settings.objects.get(id='chat_id').value)

    if is_available:
        message = f'{proxy.info} proxy is up\n{ip}\n{proxy.host}:{proxy.port}\n{info if info else ""}'
    else:
        message = f'{proxy.info} proxy is down\n{proxy.host}:{proxy.port}\n{info if info else ""}'

    if sms:
        message += f'\n\n{sms}'

    try:
        TeleBot(bot_token).send_message(chat_id, message)
    except Exception as e:
        print(e)


def send_pay_notification(proxy: Proxy):
    bot_token =  Settings.objects.get(id='bot_token').value

    message = str(proxy.info)

    try:
        TeleBot(bot_token).send_message(proxy.user_id, message)
    except Exception as e:
        print(e)


def pay_notification_checker():
    for proxy in Proxy.objects.all():
        print("loop")
        print(proxy.last_pay + timedelta(days=proxy.pay_days_interval))
        print(date.today())

        if proxy.last_pay + timedelta(days=proxy.alert_interval_days) == date.today() and \
        proxy.user_id and \
        proxy.notifying:
            print("alert")
            Thread(target=send_pay_notification, args=(proxy,)).start()
            time.sleep(0.05)
        
        if proxy.last_pay + timedelta(days=proxy.pay_days_interval) == date.today():
            print('proxy edit')
            proxy.last_pay = date.today()
            proxy.save()



def is_available_proxy(p: Proxy, protocol: str, host: str, port: int, username: str = None, password : str = None):
    # if username:
    #     proxy = f'{protocol}://{username}:{password}@{host}:{port}'
    # else:
    e = None
    if protocol == 'http' or not username:
        proxy = f'{protocol}://{host}:{port}'
    else:
        proxy = f'{protocol}://{username}:{password}@{host}:{port}'
    proxy = {
        'http': proxy,
        'https': proxy
    }

    auth = None
    if username and protocol == 'http':
        auth = HTTPProxyAuth(username, password)

    url = Settings.objects.get(id='check_url').value

    err = 'Bad status code'
    sms = ''
    for _ in range(int(Settings.objects.get(id='recheck_count').value)):
        try:
            resp = requests.get(url, proxies=proxy, auth=auth, timeout=int(Settings.objects.get(id='timeout').value))
            print(resp.status_code, host, resp.text)
            if resp.status_code == 200:
                if resp.text.count('.') == 3:
                    ip = json.loads(resp.text).get('query')
                    return True, None, ip, ''
                else:
                    err = 'Incorrect response'
        except Exception as e:
            err = ' '.join(list(map(str, e.args)))

        time.sleep(int(Settings.objects.get(id='recheck_sleep').value))
    if p.is_available:
        try:
            reboot_modem(p)
            time.sleep(80)
        except Exception as e:
            print('reboot', e)
            err = 'Cannot connect to modem to reboot'
            return False, err, '', ''

        try:
            resp = requests.get(url, proxies=proxy, auth=auth, timeout=int(Settings.objects.get(id='timeout').value))
            print(resp.status_code, host, resp.text)
            if resp.status_code == 200:
                if resp.text.count('.') == 3:
                    ip = json.loads(resp.text).get('query')
                    return True, None, ip, ''
                else:
                    err = 'Incorrect response'
        except Exception as e:
            err = ' '.join(list(map(str, e.args)))

        sms = get_last_sms(p)

    return False, err, '', sms


def check():
    proxies = Proxy.objects.all()
    for proxy in proxies:
        proxy: Proxy
        if not proxy.monitoring:
            continue

        Thread(target=check_proxy, args=(proxy,)).start()
        time.sleep(0.05)


def check_proxy(proxy: Proxy):
    is_available, error, resp, sms = is_available_proxy(proxy, proxy.protocol.id, proxy.host, proxy.port, proxy.username, proxy.password)
    print(is_available, error, resp, sms)
    if not is_available:
        if proxy.is_available:
            send_notification(proxy, error, sms=sms)
    
        proxy_for_update = Proxy.objects.get(id=proxy.id)
        proxy_for_update.is_available = False
        proxy_for_update.response = ''
        proxy_for_update.save()
    else:
        if not proxy.is_available:
            send_notification(proxy, is_available=True, ip=resp, sms=sms)
        
        proxy_for_update = Proxy.objects.get(id=proxy.id)
        proxy_for_update.is_available = True
        proxy_for_update.response = resp
        proxy_for_update.save(force_update=True)


def check_proxy_ssh():
    for proxy in Proxy.objects.all():
        if proxy.ssh_last_execute + timedelta(minutes=proxy.ssh_execute_interval) > datetime.now() or \
        proxy.ssh_execute_interval == 0:
            continue
        Thread(target=ssh_connect, args=(proxy,)).start()
        proxy.ssh_last_execute = datetime.now()
        proxy.save()
        time.sleep(0.1)


def ssh_connect(proxy: Proxy):
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(proxy.ssh_host, proxy.ssh_port, proxy.ssh_user, proxy.ssh_password)
    client.exec_command(proxy.ssh_command)
    client.close()


def change_proxies_ip():
    proxies = Proxy.objects.all()
    for proxy in proxies:
        if not proxy.monitoring:
            continue
        if proxy.ip_change_interval == 0:
            continue

        print(proxy.last_ip_change_time + timedelta(seconds=proxy.ip_change_interval))
        print(utc.localize(datetime.now()))
        if proxy.last_ip_change_time + timedelta(seconds=proxy.ip_change_interval) > datetime.now():
            continue
        
        proxy.last_ip_change_time = datetime.now()
        proxy.save()

        Thread(target=change_proxy_ip, args=(proxy,)).start()


scheduler = BackgroundScheduler()

job = None


if os.environ.get('status') == 'ok':
    # rp = Proxy.objects.get(pk=19)
    # print(get_last_sms(rp))
    sec = 120
    try:
        sec = Settings.objects.get(id='checking_interval').value
    except:
        pass
    job = scheduler.add_job(check, 'interval', seconds=int(sec))
    scheduler.add_job(pay_notification_checker, 'cron', hour=0, minute=14, second=0)
    scheduler.add_job(change_proxies_ip, 'interval', seconds=10)
    scheduler.add_job(check_proxy_ssh, 'interval', seconds=30)
    scheduler.start()
else:
    os.environ.setdefault('status', 'ok')
