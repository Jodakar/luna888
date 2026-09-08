import requests
import urllib3
import json
from datetime import datetime, timedelta
from app.models.settings import get_setting, set_setting
from app.utils.time_utils import moscow_now

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def _get_token():
    return get_setting('wb_token', '')

def _session():
    session = requests.Session()
    session.trust_env = False
    session.proxies = {'http': None, 'https': None}
    return session

def _headers():
    return {"Authorization": f"Bearer {_get_token()}", "Accept": "application/json"}

def sync_wb_ping():
    """Проверка соединения"""
    try:
        resp = _session().get('https://common-api.wildberries.ru/ping', headers=_headers(), timeout=30)
        return {'success': resp.status_code == 200, 'status': resp.status_code}
    except Exception as e:
        return {'error': str(e)}

def sync_wb_seller_info():
    """Информация о продавце"""
    try:
        resp = _session().get('https://common-api.wildberries.ru/api/v1/seller-info', headers=_headers(), timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            # Сохраняем в настройки
            if data.get('name'):
                set_setting('wb_seller_name', data['name'])
            if data.get('tin'):
                set_setting('wb_seller_tin', data['tin'])
            return {'success': True, 'data': data}
        return {'error': f'Status {resp.status_code}'}
    except Exception as e:
        return {'error': str(e)}

def sync_wb_orders():
    """Заказы (последние 7 дней)"""
    try:
        date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        resp = _session().get(
            'https://marketplace-api.wildberries.ru/api/v3/orders',
            headers=_headers(),
            params={'next': 0, 'limit': 1000},
            timeout=30
        )
        if resp.status_code == 200:
            orders = resp.json().get('orders', [])
            return {'success': True, 'count': len(orders), 'orders': orders}
        return {'error': f'Status {resp.status_code}: {resp.text[:200]}'}
    except Exception as e:
        return {'error': str(e)}

def sync_wb_supplies():
    """Поставки"""
    try:
        resp = _session().get(
            'https://marketplace-api.wildberries.ru/api/v3/supplies',
            headers=_headers(),
            params={'limit': 100, 'next': 0},
            timeout=30
        )
        if resp.status_code == 200:
            supplies = resp.json().get('supplies', [])
            return {'success': True, 'count': len(supplies), 'supplies': supplies}
        return {'error': f'Status {resp.status_code}'}
    except Exception as e:
        return {'error': str(e)}

def sync_wb_warehouses():
    """Склады"""
    try:
        resp = _session().get('https://marketplace-api.wildberries.ru/api/v3/warehouses', headers=_headers(), timeout=30)
        if resp.status_code == 200:
            warehouses = resp.json()
            return {'success': True, 'count': len(warehouses), 'warehouses': warehouses}
        return {'error': f'Status {resp.status_code}'}
    except Exception as e:
        return {'error': str(e)}

def sync_wb_sales():
    """Продажи (последние 7 дней)"""
    try:
        date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        resp = _session().get(
            'https://statistics-api.wildberries.ru/api/v1/supplier/sales',
            headers=_headers(),
            params={'dateFrom': date_from},
            timeout=30
        )
        if resp.status_code == 200:
            sales = resp.json()
            return {'success': True, 'count': len(sales), 'sales': sales}
        return {'error': f'Status {resp.status_code}: {resp.text[:200]}'}
    except Exception as e:
        return {'error': str(e)}

def sync_wb_prices():
    """Цены (по артикулам из БД)"""
    try:
        from app.models.product import Product
        # Получаем артикулы WB из БД
        nm_ids = []
        # Здесь нужен маппинг product → nmId
        # Пока пусто
        return {'success': True, 'count': 0}
    except Exception as e:
        return {'error': str(e)}

def sync_wb_returns():
    """Возвраты"""
    try:
        resp = _session().get(
            'https://returns-api.wildberries.ru/api/v1/claims',
            headers=_headers(),
            params={'is_archive': 'false', 'limit': 100},
            timeout=30
        )
        if resp.status_code == 200:
            claims = resp.json().get('claims', [])
            return {'success': True, 'count': len(claims)}
        return {'error': f'Status {resp.status_code}: {resp.text[:200]}'}
    except Exception as e:
        return {'error': str(e)}

def sync_wb_all():
    """Полная синхронизация WB"""
    results = {
        'ping': sync_wb_ping(),
        'seller': sync_wb_seller_info(),
        'orders': sync_wb_orders(),
        'supplies': sync_wb_supplies(),
        'warehouses': sync_wb_warehouses(),
        'sales': sync_wb_sales(),
        'prices': sync_wb_prices(),
        'returns': sync_wb_returns(),
        'sync_time': moscow_now().isoformat()
    }
    return results
