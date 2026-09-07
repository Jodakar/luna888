from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    variant_id = db.Column(db.String(100), unique=True, index=True)
    article = db.Column(db.String(255), index=True)
    size = db.Column(db.String(10))
    code = db.Column(db.String(50))
    barcode = db.Column(db.String(50), index=True)
    brand = db.Column(db.String(50))
    name = db.Column(db.String(255))
    kiz_count = db.Column(db.Integer, default=0)
    buy_price = db.Column(db.Float, default=0)  # в копейках
    sale_price = db.Column(db.Float, default=0)  # в копейках
    is_active = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'variant_id': self.variant_id,
            'article': self.article,
            'size': self.size,
            'code': self.code,
            'barcode': self.barcode,
            'brand': self.brand,
            'name': self.name,
            'kiz_count': self.kiz_count,
            'buy_price': self.buy_price,
            'sale_price': self.sale_price,
            'is_active': self.is_active,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ProductStock(db.Model):
    __tablename__ = 'product_stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), index=True)
    store_name = db.Column(db.String(100))  # Основной, WB FBS, Ozon FBS, DBS WB
    stock = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    product = db.relationship('Product', backref='stocks')
