from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.user import User, Permission, NotificationSetting
from app import db
from datetime import datetime
from app.utils.time_utils import moscow_now
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

employees_bp = Blueprint('employees', __name__)

# Список модулей для прав
MODULES = [
    'products', 'orders_supplier', 'orders_mp', 'couriers', 
    'deliveries', 'returns', 'inventory', 'reports', 
    'timesheet', 'employees', 'settings'
]

# Список событий для уведомлений
EVENTS = [
    'new_order', 'order_shipped', 'order_cancelled', 'inventory_check',
    'return_received', 'courier_assigned', 'delivery_created', 'delivery_completed'
]

def send_temp_password(email, password, full_name):
    """Отправка временного пароля на почту"""
    try:
        msg = MIMEMultipart()
        msg['From'] = 'matsiew@yandex.ru'
        msg['To'] = email
        msg['Subject'] = '🌙 Luna888: Доступ к системе'
        
        body = f"""Здравствуйте, {full_name}!

Ваш временный пароль: {password}

Логин: {email}

Рекомендуем сменить пароль после первого входа.
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

@employees_bp.route('/employees')
@login_required
def index():
    employees = User.query.filter_by(is_active=True).all()
    return render_template('employees/index.html', employees=employees)

@employees_bp.route('/employees/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        telegram = request.form.get('telegram', '').strip()
        position = request.form.get('position', '').strip()
        
        # Проверяем, что email не занят
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash('Сотрудник с таким email уже существует', 'error')
            return redirect(url_for('employees.add_employee'))
        
        # Генерируем временный пароль
        temp_password = str(random.randint(100000, 999999))
        
        # Создаём сотрудника
        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            telegram=telegram,
            whatsapp=phone,
            position=position,
            is_active=True
        )
        user.set_password(temp_password)
        db.session.add(user)
        db.session.commit()
        
        # Сохраняем права
        for module in MODULES:
            perm = Permission(
                user_id=user.id,
                module=module,
                can_view=False,
                can_edit=False
            )
            db.session.add(perm)
        db.session.commit()
        
        # Отправляем пароль
        if send_temp_password(email, temp_password, full_name):
            flash('Сотрудник создан! Временный пароль отправлен на почту.', 'success')
        else:
            flash(f'Сотрудник создан! Временный пароль: {temp_password}', 'warning')
        
        return redirect(url_for('employees.index'))
    
    return render_template('employees/add.html')

@employees_bp.route('/employees/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_employee(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.full_name = request.form.get('full_name', '').strip()
        user.phone = request.form.get('phone', '').strip()
        user.telegram = request.form.get('telegram', '').strip()
        user.position = request.form.get('position', '').strip()
        
        # Сохраняем права
        for module in MODULES:
            perm = Permission.query.filter_by(user_id=user.id, module=module).first()
            if not perm:
                perm = Permission(user_id=user.id, module=module)
                db.session.add(perm)
            
            perm.can_view = bool(request.form.get(f'view_{module}'))
            perm.can_edit = bool(request.form.get(f'edit_{module}'))
        
        db.session.commit()
        flash('Данные обновлены', 'success')
        return redirect(url_for('employees.index'))
    
    # Получаем права
    permissions = {}
    for perm in user.permissions_list:
        permissions[perm.module] = perm
    
    return render_template('employees/edit.html', user=user, permissions=permissions, modules=MODULES)

@employees_bp.route('/employees/<int:user_id>/toggle', methods=['POST'])
@login_required
def toggle_employee(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'разблокирован' if user.is_active else 'заблокирован'
    flash(f'Сотрудник {status}', 'success')
    return redirect(url_for('employees.index'))

@employees_bp.route('/employees/<int:user_id>/notifications', methods=['GET', 'POST'])
@login_required
def notifications(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.preferred_notification = request.form.get('preferred_notification', 'email')
        db.session.commit()
        flash('Способ уведомления обновлён', 'success')
        return redirect(url_for('employees.index'))
    
    return render_template('employees/notifications.html', user=user)
