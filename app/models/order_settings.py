from app import db
from datetime import datetime
from app.utils.time_utils import moscow_now

class OrderSettings(db.Model):
    __tablename__ = 'order_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    min_stock = db.Column(db.Integer, default=3)
    delivery_days = db.Column(db.Integer, default=7)
    sales_period = db.Column(db.String(10), default='30')
    supplier_id = db.Column(db.Integer)  # ID поставщика
    updated_at = db.Column(db.DateTime, default=moscow_now(), onupdate=moscow_now())
    
    def to_dict(self):
        return {
            'min_stock': self.min_stock,
            'delivery_days': self.delivery_days,
            'sales_period': self.sales_period,
            'supplier_id': self.supplier_id
        }
