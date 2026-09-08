from app import db
from app.utils.time_utils import moscow_now

class WBOrder(db.Model):
    __tablename__ = 'wb_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    wb_order_id = db.Column(db.String(50), unique=True, index=True)
    order_uid = db.Column(db.String(100))
    article = db.Column(db.String(255), index=True)
    nm_id = db.Column(db.Integer, index=True)
    barcode = db.Column(db.String(50), index=True)
    status = db.Column(db.String(20), index=True)
    supply_id = db.Column(db.String(50))
    price = db.Column(db.Float, default=0)
    warehouse_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    synced_at = db.Column(db.DateTime, default=moscow_now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'wb_order_id': self.wb_order_id,
            'order_uid': self.order_uid,
            'article': self.article,
            'nm_id': self.nm_id,
            'barcode': self.barcode,
            'status': self.status,
            'price': self.price,
            'warehouse_id': self.warehouse_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'synced_at': self.synced_at.isoformat() if self.synced_at else None
        }

class WBSale(db.Model):
    __tablename__ = 'wb_sales'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.String(50), unique=True, index=True)
    article = db.Column(db.String(255), index=True)
    nm_id = db.Column(db.Integer, index=True)
    barcode = db.Column(db.String(50))
    size = db.Column(db.String(10))
    total_price = db.Column(db.Float, default=0)
    for_pay = db.Column(db.Float, default=0)
    sale_date = db.Column(db.DateTime)
    synced_at = db.Column(db.DateTime, default=moscow_now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'sale_id': self.sale_id,
            'article': self.article,
            'nm_id': self.nm_id,
            'barcode': self.barcode,
            'size': self.size,
            'total_price': self.total_price,
            'for_pay': self.for_pay,
            'sale_date': self.sale_date.isoformat() if self.sale_date else None,
            'synced_at': self.synced_at.isoformat() if self.synced_at else None
        }

class WBSupply(db.Model):
    __tablename__ = 'wb_supplies'
    
    id = db.Column(db.Integer, primary_key=True)
    supply_id = db.Column(db.String(50), unique=True, index=True)
    name = db.Column(db.String(255))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)
    synced_at = db.Column(db.DateTime, default=moscow_now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'supply_id': self.supply_id,
            'name': self.name,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'synced_at': self.synced_at.isoformat() if self.synced_at else None
        }

class WBReturn(db.Model):
    __tablename__ = 'wb_returns'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.String(50), unique=True, index=True)
    order_id = db.Column(db.String(50))
    article = db.Column(db.String(255), index=True)
    nm_id = db.Column(db.Integer)
    barcode = db.Column(db.String(50))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    synced_at = db.Column(db.DateTime, default=moscow_now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'claim_id': self.claim_id,
            'order_id': self.order_id,
            'article': self.article,
            'nm_id': self.nm_id,
            'barcode': self.barcode,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'synced_at': self.synced_at.isoformat() if self.synced_at else None
        }
