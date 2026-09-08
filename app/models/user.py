from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from app.utils.time_utils import moscow_now
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    telegram = db.Column(db.String(100))
    whatsapp = db.Column(db.String(50))
    position = db.Column(db.String(100))
    preferred_notification = db.Column(db.String(20), default='email')  # email, telegram, whatsapp, sms
    is_active = db.Column(db.Boolean, default=True)
    reset_code = db.Column(db.String(6))
    reset_code_expires = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=moscow_now())
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Модель прав доступа
class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    module = db.Column(db.String(100), nullable=False)  # products, orders_mp, couriers...
    can_view = db.Column(db.Boolean, default=False)
    can_edit = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='permissions_list')

# Модель уведомлений
class NotificationSetting(db.Model):
    __tablename__ = 'notification_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    event = db.Column(db.String(100), nullable=False)  # new_order, shipment, inventory...
    email = db.Column(db.Boolean, default=False)
    telegram = db.Column(db.Boolean, default=False)
    whatsapp = db.Column(db.Boolean, default=False)
    sms = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='notification_list')
