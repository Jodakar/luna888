from app import db
from app.utils.time_utils import moscow_now

class WBProductMapping(db.Model):
    __tablename__ = 'wb_product_mapping'
    
    id = db.Column(db.Integer, primary_key=True)
    nm_id = db.Column(db.Integer, unique=True, index=True)  # Артикул WB
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), index=True)  # Товар в МойСклад
    barcode = db.Column(db.String(50), index=True)  # Штрихкод (связующее звено)
    article = db.Column(db.String(255), index=True)  # Артикул продавца
    size = db.Column(db.String(10))  # Размер
    synced_at = db.Column(db.DateTime, default=moscow_now)
    
    product = db.relationship('Product', backref='wb_mappings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nm_id': self.nm_id,
            'product_id': self.product_id,
            'barcode': self.barcode,
            'article': self.article,
            'size': self.size
        }
