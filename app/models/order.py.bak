from app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    status = db.Column(db.String(20), default='pending')  # pending, confirmed
    delivery_date = db.Column(db.DateTime)
    confirmation_link = db.Column(db.String(200), unique=True)
    supply_id = db.Column(db.String(100))
    is_sent = db.Column(db.Boolean, default=False)
    min_stock = db.Column(db.Integer, default=3)
    delivery_days = db.Column(db.Integer, default=7)
    sales_period = db.Column(db.String(10), default='30')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    supplier = db.relationship('Supplier', backref='orders')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else '',
            'status': self.status,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'min_stock': self.min_stock,
            'is_sent': self.is_sent,
            'delivery_days': self.delivery_days,
            'sales_period': self.sales_period
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, default=0)
    
    order = db.relationship('Order', backref='items')
    product = db.relationship('Product', backref='order_items')
