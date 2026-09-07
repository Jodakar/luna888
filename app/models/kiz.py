from app import db
from datetime import datetime

class KIZ(db.Model):
    __tablename__ = 'kizs'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), index=True)
    cis = db.Column(db.String(255), unique=True, index=True)  # Полный КИЗ
    gtin = db.Column(db.String(14))  # GTIN из КИЗа
    serial = db.Column(db.String(100))  # Серийный номер
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref='kiz_list')
    
    def to_dict(self):
        return {
            'cis': self.cis,
            'gtin': self.gtin,
            'serial': self.serial
        }
