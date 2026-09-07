#!/usr/bin/env python3
"""
📊 Мониторинг синхронизации
Проверяет last_sync каждые 10 минут
Уведомляет в Telegram при сбоях
"""

import os
import time
import requests
from datetime import datetime, timedelta, timezone

SYNC_FILE = '/var/www/luna888/last_sync.txt'
TELEGRAM_TOKEN = '8813254550:AAHIlJA8ANnePZmbgLUdpf8Qy5KaMutaSo8'
TELEGRAM_CHAT_ID = ''  # Нужно получить через getUpdates

STATE_FILE = '/var/www/luna888/sync_monitor_state.json'

def send_telegram(message):
    """Отправка в Telegram"""
    if not TELEGRAM_CHAT_ID:
        print("Chat ID не настроен")
        return
    
    try:
        requests.post(
            f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',
            json={'chat_id': TELEGRAM_CHAT_ID, 'text': message},
            timeout=10
        )
    except Exception as e:
        print(f"Ошибка Telegram: {e}")

def get_last_sync():
    """Получение времени последней синхронизации"""
    if os.path.exists(SYNC_FILE):
        with open(SYNC_FILE, 'r') as f:
            return f.read().strip()
    return None

def get_state():
    """Получение состояния"""
    import json
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {'was_error': False}

def save_state(state):
    """Сохранение состояния"""
    import json
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def main():
    moscow = timezone(timedelta(hours=3))
    now = datetime.now(moscow)
    
    last_sync_str = get_last_sync()
    state = get_state()
    
    if not last_sync_str:
        print(f"[{now}] last_sync не найден")
        return
    
    try:
        last_sync = datetime.fromisoformat(last_sync_str)
    except:
        print(f"[{now}] Неверный формат: {last_sync_str}")
        return
    
    # Проверяем, прошло ли больше 15 минут
    time_diff = now - last_sync
    minutes_diff = time_diff.total_seconds() / 60
    
    if minutes_diff > 15:
        if not state.get('was_error'):
            msg = f"❌ Luna888: Синхронизация не работает!\nПоследняя: {last_sync_str}\nПроверка: {now}"
            send_telegram(msg)
            print(f"[{now}] ❌ Отправлено уведомление о сбое")
        state['was_error'] = True
    else:
        if state.get('was_error'):
            msg = f"✅ Luna888: Синхронизация восстановлена!\nВремя: {now}"
            send_telegram(msg)
            print(f"[{now}] ✅ Отправлено уведомление о восстановлении")
        state['was_error'] = False
        print(f"[{now}] ✅ Синхронизация работает (последняя: {minutes_diff:.1f} мин назад)")
    
    save_state(state)

if __name__ == '__main__':
    main()
