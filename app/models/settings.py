from app import db
from datetime import datetime
from app.utils.time_utils import moscow_now
from cryptography.fernet import Fernet
import os

class Settings(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    is_encrypted = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=moscow_now, onupdate=moscow_now)

def get_encryption_key():
    """Ключ шифрования"""
    key_file = '/var/www/luna888/.secret_key'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        return key

def encrypt_value(value):
    """Шифрование"""
    key = get_encryption_key()
    fernet = Fernet(key)
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(value):
    """Дешифрование"""
    key = get_encryption_key()
    fernet = Fernet(key)
    return fernet.decrypt(value.encode()).decode()

def get_setting(key, default=None):
    """Получение настройки"""
    setting = Settings.query.filter_by(key=key).first()
    if not setting:
        return default
    if setting.is_encrypted:
        return decrypt_value(setting.value)
    return setting.value

def set_setting(key, value, is_encrypted=False):
    """Сохранение настройки"""
    setting = Settings.query.filter_by(key=key).first()
    if not setting:
        setting = Settings(key=key)
        db.session.add(setting)
    
    if is_encrypted:
        setting.value = encrypt_value(value)
        setting.is_encrypted = True
    else:
        setting.value = value
        setting.is_encrypted = False
    
    db.session.commit()
