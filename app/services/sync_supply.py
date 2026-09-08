import requests
import urllib3
from app.models.settings import get_setting

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

STORE_ID = '3b6c7c51-a05e-11f1-0a80-11bb00080e59'
ORGANIZATION_ID = '3b6aff87-a05e-11f1-0a80-11bb00080e56'
AGENT_ID = '3b6cae10-a05e-11f1-0a80-11bb00080e5a'  # ООО "Поставщик"

def create_supply(order_number, items, token=None):
    """Создание приёмки в МойСклад"""
    if not token:
        from app.models.settings import get_setting
        token = get_setting('moysklad_token')
    if not token:
        return {'error': 'Токен не указан'}
    
    session = requests.Session()
    session.trust_env = False
    session.proxies = {'http': None, 'https': None}
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json;charset=utf-8", "Content-Type": "application/json"}
    
    # Создаём позиции
    positions = []
    for item in items:
        positions.append({
            "quantity": item['quantity'],
            "price": item.get('price', 0),
            "assortment": {
                "meta": {
                    "href": f"https://api.moysklad.ru/api/remap/1.2/entity/variant/{item['variant_id']}",
                    "type": "variant",
                    "mediaType": "application/json"
                }
            }
        })
    
    # Данные приёмки
    supply_data = {
        "name": f"Заказ {order_number}",
        "applicable": False,  # Черновик без проведения
        "organization": {
            "meta": {
                "href": f"https://api.moysklad.ru/api/remap/1.2/entity/organization/{ORGANIZATION_ID}",
                "type": "organization",
                "mediaType": "application/json"
            }
        },
        "agent": {
            "meta": {
                "href": f"https://api.moysklad.ru/api/remap/1.2/entity/counterparty/{AGENT_ID}",
                "type": "counterparty",
                "mediaType": "application/json"
            }
        },
        "store": {
            "meta": {
                "href": f"https://api.moysklad.ru/api/remap/1.2/entity/store/{STORE_ID}",
                "type": "store",
                "mediaType": "application/json"
            }
        },
        "positions": positions
    }
    
    response = session.post(
        'https://api.moysklad.ru/api/remap/1.2/entity/supply',
        headers=headers, json=supply_data, verify=False, timeout=60
    )
    
    if response.status_code in [200, 201]:
        supply = response.json()
        return {'success': True, 'supply_id': supply.get('id')}
    else:
        return {'error': f'Ошибка {response.status_code}: {response.text[:200]}'}

def delete_supply(supply_id, token=None):
    """Удаление приёмки из МойСклад"""
    if not token:
        from app.models.settings import get_setting
        token = get_setting('moysklad_token')
    if not token:
        return {'error': 'Токен не указан'}
    
    session = requests.Session()
    session.trust_env = False
    session.proxies = {'http': None, 'https': None}
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json;charset=utf-8"}
    
    response = session.delete(
        f'https://api.moysklad.ru/api/remap/1.2/entity/supply/{supply_id}',
        headers=headers, verify=False, timeout=60
    )
    
    if response.status_code == 200:
        return {'success': True}
    else:
        return {'error': f'Ошибка {response.status_code}: {response.text[:200]}'}
