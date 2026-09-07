from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.models.settings import get_setting, set_setting
from app.services.monitor import check_all_tokens

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
@login_required
def index():
    # Получаем текущие настройки
    settings = {
        'moysklad_token': get_setting('moysklad_token', ''),
        'wb_token': get_setting('wb_token', ''),
        'ozon_client_id': get_setting('ozon_client_id', ''),
        'ozon_api_key': get_setting('ozon_api_key', ''),
        'telegram_bot_token': get_setting('telegram_bot_token', ''),
        'smtp_host': get_setting('smtp_host', 'smtp.yandex.ru'),
        'smtp_port': get_setting('smtp_port', '465'),
        'smtp_user': get_setting('smtp_user', 'matsiew@yandex.ru'),
    'smtp_from_name': get_setting('smtp_from_name', 'Luna888'),
        'smtp_password': get_setting('smtp_password', ''),
        'smtp_to': get_setting('smtp_to', 'jodakar@vk.com'),
    }
    
    # Проверяем токены
    statuses = check_all_tokens()
    
    return render_template('settings/index.html', settings=settings, statuses=statuses)

@settings_bp.route('/settings/save', methods=['POST'])
@login_required
def save():
    # Сохраняем API-ключи (зашифрованные)
    set_setting('moysklad_token', request.form.get('moysklad_token', ''), is_encrypted=True)
    set_setting('wb_token', request.form.get('wb_token', ''), is_encrypted=True)
    set_setting('ozon_client_id', request.form.get('ozon_client_id', ''), is_encrypted=True)
    set_setting('ozon_api_key', request.form.get('ozon_api_key', ''), is_encrypted=True)
    set_setting('telegram_bot_token', request.form.get('telegram_bot_token', ''), is_encrypted=True)
    
    # SMTP
    set_setting('smtp_host', request.form.get('smtp_host', 'smtp.yandex.ru'))
    set_setting('smtp_port', request.form.get('smtp_port', '465'))
    set_setting('smtp_user', request.form.get('smtp_user', ''))
    set_setting('smtp_from_name', request.form.get('smtp_from_name', 'Luna888'))
    set_setting('smtp_password', request.form.get('smtp_password', ''), is_encrypted=True)
    set_setting('smtp_to', request.form.get('smtp_to', ''))
    
    flash('Настройки сохранены', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/settings/check-tokens')
@login_required
def check_tokens():
    statuses = check_all_tokens()
    return render_template('settings/check_result.html', statuses=statuses)
