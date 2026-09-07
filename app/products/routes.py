from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.services.sync_products import sync_from_moysklad, get_products_from_db
from datetime import datetime, timezone, timedelta
import os

products_bp = Blueprint('products', __name__)

SYNC_FILE = '/var/www/luna888/last_sync.txt'

def get_moscow_time():
    """Текущее московское время ISO"""
    moscow = timezone(timedelta(hours=3))
    return datetime.now(moscow).isoformat()

def get_last_sync():
    if os.path.exists(SYNC_FILE):
        with open(SYNC_FILE, 'r') as f:
            return f.read().strip()
    return None

def set_last_sync(time_str=None):
    if not time_str:
        time_str = get_moscow_time()
    with open(SYNC_FILE, 'w') as f:
        f.write(time_str)

@products_bp.route('/products')
@login_required
def index():
    return render_template('products/index.html')

@products_bp.route('/products/api/data')
@login_required
def api_data():
    products = get_products_from_db(include_inactive=False)
    
    return jsonify({
        'products': products,
        'last_sync': get_last_sync(),
        'count': len(products)
    })

@products_bp.route('/products/api/sync')
@login_required
def api_sync():
    result = sync_from_moysklad()
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 400
    
    # Устанавливаем московское время
    set_last_sync()
    
    return jsonify({
        'success': True,
        'count': result.get('count', 0),
        'sync_time': get_last_sync()
    })
