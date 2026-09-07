from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
from datetime import datetime, timedelta
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

auth_bp = Blueprint('auth', __name__)

def send_reset_email(email, code):
    """Отправка кода восстановления на почту"""
    try:
        msg = MIMEMultipart()
        msg['From'] = 'matsiew@yandex.ru'
        msg['To'] = email
        msg['Subject'] = '🌙 Luna888: Восстановление пароля'
        
        body = f"""Здравствуйте!

Ваш код для восстановления пароля: {code}

Если вы не запрашивали восстановление, проигнорируйте это письмо.
"""
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP_SSL('smtp.yandex.ru', 465, timeout=15)
        server.login('matsiew@yandex.ru', 'gnrmznxwltxyvgzb')
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return False

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('products.index'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email, is_active=True).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('products.index'))
        
        flash('Неверный email или пароль', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()
        
        if user:
            code = str(random.randint(100000, 999999))
            user.reset_code = code
            user.reset_code_expires = datetime.utcnow() + timedelta(minutes=15)
            db.session.commit()
            
            if send_reset_email(email, code):
                flash('Код отправлен на почту', 'success')
            else:
                flash('Ошибка отправки кода', 'error')
        else:
            flash('Пользователь не найден', 'error')
        
        return redirect(url_for('auth.reset_confirm', email=email))
    
    return render_template('auth/reset_password.html')

@auth_bp.route('/reset-confirm/<email>', methods=['GET', 'POST'])
def reset_confirm(email):
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        new_password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.reset_code == code and user.reset_code_expires > datetime.utcnow():
            user.set_password(new_password)
            user.reset_code = None
            user.reset_code_expires = None
            db.session.commit()
            flash('Пароль обновлён! Войдите с новым паролем.', 'success')
            return redirect(url_for('auth.login'))
        
        flash('Неверный код или истёк срок действия', 'error')
    
    return render_template('auth/reset_confirm.html', email=email)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
