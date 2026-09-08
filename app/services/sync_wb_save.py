from app import db
from app.models.wb import WBOrder, WBSale, WBSupply, WBReturn
from app.services.sync_wb import sync_wb_all, sync_wb_supplies
from datetime import datetime
from app.utils.time_utils import moscow_now

def save_wb_data():
    """Синхронизация и сохранение в БД"""
    results = sync_wb_all()
    
    # Сохраняем заказы
    if 'success' in results.get('orders', {}):
        for order in results['orders'].get('orders', []):
            existing = WBOrder.query.filter_by(wb_order_id=str(order.get('id'))).first()
            if not existing:
                existing = WBOrder(wb_order_id=str(order.get('id')))
                db.session.add(existing)
            
            existing.order_uid = order.get('orderUid', '')
            existing.supply_id = order.get('supplyId', '')
            existing.article = order.get('article', '')
            existing.nm_id = order.get('nmId')
            existing.barcode = ','.join(order.get('skus', []))
            existing.status = order.get('status', 'new')
            existing.price = order.get('price', 0) / 100
            existing.warehouse_id = order.get('warehouseId')
            existing.created_at = datetime.fromisoformat(order.get('createdAt', '').replace('Z', '+00:00')) if order.get('createdAt') else None
            existing.synced_at = moscow_now()
    
    # Сохраняем продажи
    if 'success' in results.get('sales', {}):
        for sale in results['sales'].get('sales', []):
            existing = WBSale.query.filter_by(sale_id=sale.get('saleID')).first()
            if not existing:
                existing = WBSale(sale_id=sale.get('saleID'))
                db.session.add(existing)
            
            existing.article = sale.get('supplierArticle', '')
            existing.nm_id = sale.get('nmId')
            existing.barcode = sale.get('barcode', '')
            existing.size = sale.get('techSize', '')
            existing.total_price = sale.get('totalPrice', 0) / 100
            existing.for_pay = sale.get('forPay', 0)
            existing.sale_date = datetime.fromisoformat(sale.get('date', '').replace('Z', '+00:00')) if sale.get('date') else None
            existing.synced_at = moscow_now()
    
    # Сохраняем поставки
    if results.get('supplies', {}).get('success'):
        supplies_data = sync_wb_supplies()
        supplies_list = supplies_data.get('supplies', [])
        for supply in supplies_list:
            existing = WBSupply.query.filter_by(supply_id=supply.get('id')).first()
            if not existing:
                existing = WBSupply(supply_id=supply.get('id'))
                db.session.add(existing)
            
            existing.name = supply.get('name', '')
            existing.status = 'done' if supply.get('done') else 'active'
            existing.created_at = datetime.fromisoformat(supply.get('createdAt', '').replace('Z', '+00:00')) if supply.get('createdAt') else None
            existing.synced_at = moscow_now()
    
    db.session.commit()
    return {'success': True, 'sync_time': moscow_now().isoformat()}
