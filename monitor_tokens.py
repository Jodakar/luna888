#!/usr/bin/env python3
"""
🔍 Мониторинг токенов каждые 5 минут
Только существующие токены
Уведомления при сбоях и восстановлении
"""

import sys
import os
import json
import time
import requests
import urllib3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

sys.path.insert(0, '/var/www/luna888')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Файл состояния
STATE_FILE = '/var/www/luna888/token_status.json'

# SMTP
SMTP_HOST = 'smtp.yandex.ru'
SMTP_PORT = 465
SMTP_USER = 'matsiew@yandex.ru'
SMTP_PASSWORD = 'gnrmznxwltxyvgzb'
SMTP_TO = 'jodakar@vk.com'

def load_settings():
    """Загрузка настроек из БД"""
    from app import create_app
    from app.models.settings import get_setting
    
    app = create_app()
    with app.app_context():
        return {
            'moysklad_token': get_setting('moysklad_token'),
            'wb_token': get_setting('wb_token'),
            'ozon_client_id': get_setting('ozon_client_id'),
            'ozon_api_key': get_setting('ozon_api_key'),
        }

def check_moysklad(token):
    """Проверка МойСклад"""
    session = requests.Session()
    session.trust_env = False
    session.proxies = {'http': None, 'https': None}
    
    try:
        r = session.get(
            'https://api.moysklad.ru/api/remap/1.2/entity/product',
            headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json;charset=utf-8'},
            params={'limit': 1},
            verify=False, timeout=10
        )
        return r.status_code == 200
    except:
        return False

def check_wb(token):
    """Проверка WB"""
    session = requests.Session()
    session.trust_env = False
    session.proxies = {'http': None, 'https': None}
    
    try:
        r = session.get(
            'https://marketplace-api.wildberries.ru/ping',
            headers={'Authorization': f'Bearer {token}'},
            verify=False, timeout=10
        )
        return r.status_code == 200
    except:
        return False

def check_ozon(client_id, api_key):
    """Проверка Ozon"""
    try:
        r = requests.post(
            'https://api-seller.ozon.ru/v1/product/list',
            headers={'Client-Id': client_id, 'Api-Key': api_key, 'Content-Type': 'application/json'},
            json={'page': 1, 'page_size': 1},
            timeout=10
        )
        return r.status_code == 200
    except:
        return False

def send_email(subject, body):
    """Отправка уведомления"""
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{get_setting('smtp_from_name', 'Luna888')} <{SMTP_USER}>" if get_setting('smtp_from_name') else SMTP_USER
        msg['To'] = SMTP_TO
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return False

def load_state():
    """Загрузка состояния"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    """Сохранение состояния"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def main():
    settings = load_settings()
    state = load_state()
    now = datetime.utcnow()
    changes = []
    
    # Проверяем каждый токен (только если он указан)
    checks = [
        ('moysklad', 'МойСклад', settings.get('moysklad_token'), check_moysklad),
    ]
    
    if settings.get('wb_token'):
        checks.append(('wb', 'Wildberries', settings['wb_token'], check_wb))
    
    if settings.get('ozon_client_id') and settings.get('ozon_api_key'):
        checks.append(('ozon', 'Ozon', (settings['ozon_client_id'], settings['ozon_api_key']), check_ozon))
    
    for key, name, token, checker in checks:
        if isinstance(token, tuple):
            is_ok = checker(token[0], token[1])
        else:
            is_ok = checker(token)
        
        old_status = state.get(key)
        new_status = 'ok' if is_ok else 'error'
        
        # Обновляем состояние
        state[key] = new_status
        
        # Проверяем изменения
        if old_status and old_status != new_status:
            changes.append({
                'service': name,
                'old': old_status,
                'new': new_status
            })
    
    # Отправляем уведомления при изменениях
    for change in changes:
        if change['new'] == 'error':
            subject = f"❌ Luna888: {change['service']} недоступен"
            body = f"{change['service']} перестал отвечать.\nВремя: {now}"
            send_email(subject, body)
        elif change['new'] == 'ok' and change['old'] == 'error':
            subject = f"✅ Luna888: {change['service']} восстановлен"
            body = f"{change['service']} снова работает.\nВремя: {now}"
            send_email(subject, body)
    
    save_state(state)
    print(f"[{now}] Проверено: {len(checks)} сервисов")

if __name__ == '__main__':
    main()
