from app import db
from datetime import datetime
from app.utils.time_utils import moscow_now

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    moysklad_id = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(255), nullable=False)  # Краткое наименование
    full_name = db.Column(db.String(500))  # Полное наименование
    code = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255))
    actual_address = db.Column(db.String(500))
    legal_address = db.Column(db.String(500))
    inn = db.Column(db.String(20), index=True)
    kpp = db.Column(db.String(20))
    ogrn = db.Column(db.String(50))
    okpo = db.Column(db.String(50))
    comment = db.Column(db.Text)
    director_name = db.Column(db.String(255))
    director_position = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=moscow_now())
    updated_at = db.Column(db.DateTime, default=moscow_now(), onupdate=moscow_now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'moysklad_id': self.moysklad_id,
            'name': self.name,
            'full_name': self.full_name,
            'code': self.code,
            'phone': self.phone,
            'email': self.email,
            'actual_address': self.actual_address,
            'legal_address': self.legal_address,
            'inn': self.inn,
            'kpp': self.kpp,
            'ogrn': self.ogrn,
            'okpo': self.okpo,
            'comment': self.comment,
            'director_name': self.director_name,
            'director_position': self.director_position,
            'is_active': self.is_active
        }
