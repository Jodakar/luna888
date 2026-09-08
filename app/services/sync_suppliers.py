import requests
import urllib3
from datetime import datetime
from app import db
from app.models.supplier import Supplier
from app.models.settings import get_setting

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def sync_suppliers_from_moysklad():
    """Синхронизация поставщиков из МойСклад"""
    token = get_setting('moysklad_token')
    if not token:
        return {'error': 'Токен не указан'}
    
    session = requests.Session()
    session.trust_env = False
    session.proxies = {'http': None, 'https': None}
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json;charset=utf-8"}
    
    response = session.get(
        'https://api.moysklad.ru/api/remap/1.2/entity/counterparty',
        headers=headers, params={'limit': 100}, verify=False, timeout=60
    )
    
    if response.status_code != 200:
        return {'error': f'Ошибка: {response.status_code}'}
    
    counterparts = response.json().get('rows', [])
    synced = 0
    
    for cp in counterparts:
        cp_id = cp.get('id')
        
        supplier = Supplier.query.filter_by(moysklad_id=cp_id).first()
        if not supplier:
            supplier = Supplier(moysklad_id=cp_id)
            db.session.add(supplier)
        
        supplier.name = cp.get('name', '')
        supplier.full_name = cp.get('legalTitle', '') or cp.get('name', '')
        supplier.inn = cp.get('inn', '')
        supplier.kpp = cp.get('kpp', '')
        supplier.ogrn = cp.get('ogrn', '')
        supplier.okpo = cp.get('okpo', '')
        supplier.phone = cp.get('phone', '')
        supplier.email = cp.get('email', '')
        supplier.actual_address = cp.get('actualAddress', '')
        supplier.legal_address = cp.get('legalAddress', '')
        supplier.is_active = True
        
        synced += 1
    
    db.session.commit()
    return {'success': True, 'count': synced}
