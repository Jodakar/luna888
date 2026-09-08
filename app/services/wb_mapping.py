from app import db
from app.models.wb_mapping import WBProductMapping
from app.models.product import Product
from app.models.wb import WBOrder, WBSale
from app.utils.time_utils import moscow_now

def create_mapping_from_barcodes():
    """Создаём маппинг по баркодам из заказов и продаж"""
    
    # Собираем все баркоды из WB
    wb_barcodes = set()
    
    # Из заказов
    for order in WBOrder.query.all():
        if order.barcode:
            for bc in order.barcode.split(','):
                bc = bc.strip()
                if bc:
                    wb_barcodes.add(bc)
    
    # Из продаж
    for sale in WBSale.query.all():
        if sale.barcode:
            wb_barcodes.add(sale.barcode.strip())
    
    # Находим товары в МойСклад по баркоду
    mapped = 0
    for barcode in wb_barcodes:
        product = Product.query.filter_by(barcode=barcode).first()
        if not product:
            # Пробуем с ведущим 0
            if len(barcode) == 13:
                product = Product.query.filter_by(barcode='0' + barcode).first()
        
        if product:
            # Находим nm_id
            nm_id = None
            order = WBOrder.query.filter(WBOrder.barcode.like(f'%{barcode}%')).first()
            if order:
                nm_id = order.nm_id
            else:
                sale = WBSale.query.filter_by(barcode=barcode).first()
                if sale:
                    nm_id = sale.nm_id
            
            if nm_id:
                existing = WBProductMapping.query.filter_by(nm_id=nm_id).first()
                if not existing:
                    existing = WBProductMapping(
                        nm_id=nm_id,
                        product_id=product.id,
                        barcode=barcode,
                        article=product.article,
                        size=product.size
                    )
                    db.session.add(existing)
                    mapped += 1
    
    db.session.commit()
    return {'success': True, 'mapped': mapped, 'total_barcodes': len(wb_barcodes)}

def get_mapping():
    """Получить все маппинги"""
    return WBProductMapping.query.all()
