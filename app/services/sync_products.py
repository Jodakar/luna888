import requests
import urllib3
import re
import time
from datetime import datetime
from app.utils.time_utils import moscow_now
from app import db
from app.models.product import Product, ProductStock
from app.models.kiz import KIZ
from app.models.settings import get_setting

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

STORE_IDS = {
    '3b6c7c51-a05e-11f1-0a80-11bb00080e59': 'Основной',
    '1bc11777-a070-11f1-0a80-0f0c000d915d': 'WB FBS',
    '2bbf10f4-a070-11f1-0a80-006c000e2e71': 'Ozon FBS',
    '53c5f5f7-a070-11f1-0a80-1da3000c6a51': 'DBS WB',
    'dd7767a9-aa92-11f1-0a80-1fd100fd1899': 'WB FBO',
    'dd8d94d0-aa92-11f1-0a80-0de600fb61a0': 'Ozon FBO',
}

def sync_from_moysklad():
    token = get_setting('moysklad_token')
    if not token:
        return {'error': 'Токен не указан'}
    
    session = requests.Session()
    session.trust_env = False
    session.proxies = {'http': None, 'https': None}
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json;charset=utf-8'}
    
    # 1. Остатки
    stock_response = session.get(
        'https://api.moysklad.ru/api/remap/1.2/report/stock/all',
        headers=headers, params={'limit': 1000}, verify=False, timeout=60
    )
    if stock_response.status_code != 200:
        return {'error': f'Ошибка: {stock_response.status_code}'}
    stock_rows = stock_response.json().get('rows', [])
    
    # 2. Получаем ВСЕ модификации СРАЗУ (один запрос)
    variants_cache = {}
    offset = 0
    while True:
        var_response = session.get(
            'https://api.moysklad.ru/api/remap/1.2/entity/variant',
            headers=headers, params={'limit': 100, 'offset': offset},
            verify=False, timeout=60
        )
        if var_response.status_code != 200:
            break
        batch = var_response.json().get('rows', [])
        if not batch:
            break
        for v in batch:
            variants_cache[v.get('id')] = v
        offset += 100
        if offset >= var_response.json().get('meta', {}).get('size', 0):
            break
        time.sleep(0.3)
    
    print(f"  Модификаций в кэше: {len(variants_cache)}")
    
    # 3. Получаем ВСЕ товары (родителей)
    products_cache = {}
    offset = 0
    while True:
        prod_response = session.get(
            'https://api.moysklad.ru/api/remap/1.2/entity/product',
            headers=headers, params={'limit': 100, 'offset': offset},
            verify=False, timeout=60
        )
        if prod_response.status_code != 200:
            break
        batch = prod_response.json().get('rows', [])
        if not batch:
            break
        for p in batch:
            products_cache[p.get('id')] = p
        offset += 100
        if offset >= prod_response.json().get('meta', {}).get('size', 0):
            break
        time.sleep(0.3)
    
    print(f"  Товаров в кэше: {len(products_cache)}")
    
    # 4. Приёмки (КИЗы и закупочные цены)
    supply_response = session.get(
        'https://api.moysklad.ru/api/remap/1.2/entity/supply',
        headers=headers, verify=False, timeout=60
    )
    kiz_cache = {}
    buy_price_cache = {}
    if supply_response.status_code == 200:
        for supply in supply_response.json().get('rows', []):
            pos_response = session.get(
                f"https://api.moysklad.ru/api/remap/1.2/entity/supply/{supply.get('id')}/positions",
                headers=headers, params={'limit': 1000}, verify=False, timeout=60
            )
            if pos_response.status_code == 200:
                for p in pos_response.json().get('rows', []):
                    v_href = p.get('assortment', {}).get('meta', {}).get('href', '')
                    v_id = v_href.split('/')[-1] if v_href else ''
                    if v_id:
                        kiz_cache.setdefault(v_id, []).extend(
                            [tc.get('cis', '') for tc in p.get('trackingCodes', [])]
                        )
                        buy_price_cache[v_id] = p.get('price', 0)
            time.sleep(0.2)
    
    # 5. Синхронизация
    synced_ids = []
    
    for row in stock_rows:
        stock = int(row.get('stock', 0))
        name = row.get('name', '')
        article = row.get('article', '')
        code = row.get('code', '')
        folder = row.get('folder', {}).get('name', '')
        store_href = row.get('meta', {}).get('href', '')
        
        store_name = 'Основной'
        for sid, sname in STORE_IDS.items():
            if sid in store_href:
                store_name = sname
                break
        
        v_id = row.get('meta', {}).get('href', '').split('/')[-1].split('?')[0]
        
        match = re.match(r'^(.+?)\s*\((\d+|[SML]),\s*(\d+|[SML])\)$', name)
        size = match.group(2) if match else ''
        if not size:
            match = re.match(r'^(.+?)\s*\((\d+|[SML])\)$', name)
            size = match.group(2) if match else ''
        
        barcode = ''
        sale_price = 0
        buy_price = buy_price_cache.get(v_id, 0)
        
        # Получаем из кэша
        variant = variants_cache.get(v_id)
        
        if variant:
            # Штрихкод
            for bc in variant.get('barcodes', []):
                if isinstance(bc, dict):
                    ean = bc.get('ean13', '')
                    gtin = bc.get('gtin', '')
                    if ean and ean.startswith('46'):
                        barcode = ean
                        break
                    if gtin and gtin.startswith('046'):
                        barcode = gtin[1:] if len(gtin) == 14 else gtin
                        break
            
            # Sale price
            m_sale = variant.get('salePrices', [])
            if m_sale:
                sale_price = m_sale[0].get('value', 0)
            
            # Из родителя
            p_href = variant.get('product', {}).get('meta', {}).get('href', '')
            p_id = p_href.split('/')[-1] if p_href else ''
            parent = products_cache.get(p_id)
            
            if parent:
                if not sale_price:
                    p_sale = parent.get('salePrices', [])
                    if p_sale:
                        sale_price = p_sale[0].get('value', 0)
                if not buy_price:
                    buy_price = parent.get('buyPrice', {}).get('value', 0)
                if not barcode:
                    for bc in parent.get('barcodes', []):
                        if isinstance(bc, dict) and bc.get('ean13', '').startswith('46'):
                            barcode = bc.get('ean13', '')
                            break
        
        # Сохраняем
        product = Product.query.filter_by(variant_id=v_id).first()
        if not product:
            product = Product(variant_id=v_id)
            db.session.add(product)
        
        product.article = article
        product.size = size
        product.code = code
        product.barcode = barcode
        product.brand = folder
        product.name = name
        product.kiz_count = len(kiz_cache.get(v_id, []))
        product.buy_price = buy_price
        product.sale_price = sale_price
        product.is_active = True
        product.last_seen = moscow_now()()
        
        synced_ids.append(product.id)
        db.session.flush()
        
        # Сохраняем КИЗы
        kiz_list = kiz_cache.get(v_id, [])
        if kiz_list:
            for cis in kiz_list:
                existing_kiz = KIZ.query.filter_by(cis=cis).first()
                if not existing_kiz:
                    # Извлекаем GTIN и серийный номер
                    gtin = cis[2:16] if len(cis) > 16 else ''
                    serial = cis[18:] if len(cis) > 18 else ''
                    
                    kiz = KIZ(
                        product_id=product.id,
                        cis=cis,
                        gtin=gtin,
                        serial=serial
                    )
                    db.session.add(kiz)
        
        stock_record = ProductStock.query.filter_by(product_id=product.id, store_name=store_name).first()
        if not stock_record:
            stock_record = ProductStock(product_id=product.id, store_name=store_name)
            db.session.add(stock_record)
        stock_record.stock = stock
        stock_record.updated_at = moscow_now()()
    
    db.session.commit()
    return {'success': True, 'count': len(synced_ids), 'sync_time': moscow_now()().isoformat()}


def get_products_from_db(include_inactive=True):
    query = Product.query
    if not include_inactive:
        query = query.filter_by(is_active=True)
    
    result = []
    for product in query.all():
        data = product.to_dict()
        stocks = {s.store_name: s.stock for s in product.stocks}
        data['stocks'] = stocks
        data['total_stock'] = sum(stocks.values())
        
        # КИЗы
        kiz_list = []
        for kiz in product.kiz_list[:100]:  # Ограничиваем для скорости
            kiz_list.append(kiz.cis)
        data['kiz_list'] = kiz_list
        
        result.append(data)
    return result
