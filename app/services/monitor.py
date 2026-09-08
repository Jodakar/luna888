import requests
import urllib3
from datetime import datetime
from app.utils.time_utils import moscow_now
from app.models.settings import get_setting

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_moysklad_token():
    """Проверка токена МойСклад"""
    token = get_setting('moysklad_token')
    if not token:
        return {'status': 'not_set', 'message': 'Токен не указан'}
    
    try:
        session = requests.Session()
        session.trust_env = False
        session.proxies = {'http': None, 'https': None}
        
        response = session.get(
            'https://api.moysklad.ru/api/remap/1.2/entity/product',
            headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json;charset=utf-8'},
            params={'limit': 1},
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            return {'status': 'ok', 'message': 'Работает'}
        elif response.status_code == 401:
            return {'status': 'error', 'message': 'Неверный токен'}
        else:
            return {'status': 'error', 'message': f'Ошибка {response.status_code}'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)[:50]}

def check_wb_token():
    """Проверка токена WB"""
    token = get_setting('wb_token')
    if not token:
        return {'status': 'not_set', 'message': 'Токен не указан'}
    
    try:
        session = requests.Session()
        session.trust_env = False
        session.proxies = {'http': None, 'https': None}
        
        response = session.get(
            'https://marketplace-api.wildberries.ru/ping',
            headers={'Authorization': f'Bearer {token}'},
            timeout=10,
            verify=False
        )
        
        if response.status_code == 200:
            return {'status': 'ok', 'message': 'Работает'}
        elif response.status_code == 401:
            return {'status': 'error', 'message': 'Неверный токен'}
        else:
            return {'status': 'error', 'message': f'Ошибка {response.status_code}'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)[:50]}

def check_ozon_token():
    """Проверка токена Ozon"""
    client_id = get_setting('ozon_client_id')
    api_key = get_setting('ozon_api_key')
    
    if not client_id or not api_key:
        return {'status': 'not_set', 'message': 'Токены не указаны'}
    
    try:
        response = requests.post(
            'https://api-seller.ozon.ru/v1/product/list',
            headers={
                'Client-Id': client_id,
                'Api-Key': api_key,
                'Content-Type': 'application/json'
            },
            json={'page': 1, 'page_size': 1},
            timeout=10
        )
        
        if response.status_code == 200:
            return {'status': 'ok', 'message': 'Работает'}
        elif response.status_code == 401:
            return {'status': 'error', 'message': 'Неверные токены'}
        else:
            return {'status': 'error', 'message': f'Ошибка {response.status_code}'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)[:50]}

def check_all_tokens():
    """Проверка всех токенов"""
    return {
        'moysklad': check_moysklad_token(),
        'wb': check_wb_token(),
        'ozon': check_ozon_token(),
        'checked_at': moscow_now()().isoformat()
    }
