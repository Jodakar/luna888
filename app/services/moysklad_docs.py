from app import db
from app.models.settings import get_setting
from app.models.product import Product
import requests
import urllib3
from datetime import datetime
from app.utils.time_utils import moscow_now

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ID складов МойСклад
STORE_MAIN = '3b6c7c51-a05e-11f1-0a80-11bb00080e59'  # Основной
STORE_WB_FBS = '1bc11777-a070-11f1-0a80-0f0c000d915d'  # WB FBS
ORGANIZATION_ID = '3b6aff87-a05e-11f1-0a80-11bb00080e56'

def _get_session():
    session = requests.Session()
    session.trust_env = False
    session.proxies = {'http': None, 'https': None}
    return session

def _headers():
    token = get_setting('moysklad_token', '')
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json;charset=utf-8",
        "Content-Type": "application/json"
    }

def create_demand(items, store_id=STORE_MAIN):
    """Создание Отгрузки (Demand) в МойСклад"""
    session = _get_session()
    
    # Формируем позиции
    positions = []
    for item in items:
        variant_id = item.get('variant_id')
        quantity = item.get('quantity', 1)
        
        if variant_id:
            positions.append({
                "quantity": quantity,
                "assortment": {
                    "meta": {
                        "href": f"https://api.moysklad.ru/api/remap/1.2/entity/variant/{variant_id}",
                        "type": "variant",
                        "mediaType": "application/json"
                    }
                }
            })
    
    if not positions:
        return {'error': 'Нет позиций для отгрузки'}
    
    demand_data = {
        "organization": {
            "meta": {
                "href": f"https://api.moysklad.ru/api/remap/1.2/entity/organization/{ORGANIZATION_ID}",
                "type": "organization",
                "mediaType": "application/json"
            }
        },
        "store": {
            "meta": {
                "href": f"https://api.moysklad.ru/api/remap/1.2/entity/store/{store_id}",
                "type": "store",
                "mediaType": "application/json"
            }
        },
        "positions": positions
    }
    
    resp = session.post(
        'https://api.moysklad.ru/api/remap/1.2/entity/demand',
        headers=_headers(),
        json=demand_data,
        verify=False,
        timeout=60
    )
    
    if resp.status_code in [200, 201]:
        demand = resp.json()
        return {'success': True, 'demand_id': demand.get('id'), 'name': demand.get('name')}
    else:
        return {'error': f'Ошибка {resp.status_code}: {resp.text[:200]}'}

def create_supply(items, store_id=STORE_MAIN):
    """Создание Приёмки (Supply) в МойСклад"""
    session = _get_session()
    
    positions = []
    for item in items:
        variant_id = item.get('variant_id')
        quantity = item.get('quantity', 1)
        
        if variant_id:
            positions.append({
                "quantity": quantity,
                "assortment": {
                    "meta": {
                        "href": f"https://api.moysklad.ru/api/remap/1.2/entity/variant/{variant_id}",
                        "type": "variant",
                        "mediaType": "application/json"
                    }
                }
            })
    
    if not positions:
        return {'error': 'Нет позиций для приёмки'}
    
    supply_data = {
        "organization": {
            "meta": {
                "href": f"https://api.moysklad.ru/api/remap/1.2/entity/organization/{ORGANIZATION_ID}",
                "type": "organization",
                "mediaType": "application/json"
            }
        },
        "store": {
            "meta": {
                "href": f"https://api.moysklad.ru/api/remap/1.2/entity/store/{store_id}",
                "type": "store",
                "mediaType": "application/json"
            }
        },
        "positions": positions
    }
    
    resp = session.post(
        'https://api.moysklad.ru/api/remap/1.2/entity/supply',
        headers=_headers(),
        json=supply_data,
        verify=False,
        timeout=60
    )
    
    if resp.status_code in [200, 201]:
        supply = resp.json()
        return {'success': True, 'supply_id': supply.get('id'), 'name': supply.get('name')}
    else:
        return {'error': f'Ошибка {resp.status_code}: {resp.text[:200]}'}
