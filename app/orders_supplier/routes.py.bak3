from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.supplier import Supplier
from app.models.order import Order, OrderItem
from app.models.order_settings import OrderSettings
from app.models.product import Product
from app.models.settings import get_setting
from app import db
from datetime import datetime, timedelta
import secrets

orders_supplier_bp = Blueprint('orders_supplier', __name__)

@orders_supplier_bp.route('/orders-supplier')
@login_required
def index():
    return render_template('orders_supplier/index.html')

@orders_supplier_bp.route('/orders-supplier/new')
@login_required
def new_order():
    return render_template('orders_supplier/index.html', mode='new')

@orders_supplier_bp.route('/orders-supplier/order/<int:order_id>')
@login_required
def view_order(order_id):
    return render_template('orders_supplier/index.html', mode='view', order_id=order_id)

@orders_supplier_bp.route('/orders-supplier/order/<int:order_id>/send')
@login_required
def send_order(order_id):
    order = Order.query.get_or_404(order_id)
    supplier = Supplier.query.get(order.supplier_id)
    
    # Получаем организации из МойСклад
    token = get_setting('moysklad_token')
    organizations = []
    supplier_email = ''
    
    if token:
        import requests as req
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        session = req.Session()
        session.trust_env = False
        session.proxies = {'http': None, 'https': None}
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json;charset=utf-8"}
        
        # Организации
        response = session.get(
            'https://api.moysklad.ru/api/remap/1.2/entity/organization',
            headers=headers, verify=False, timeout=60
        )
        
        if response.status_code == 200:
            for org in response.json().get('rows', []):
                organizations.append({
                    'id': org.get('id'),
                    'name': org.get('name'),
                    'email': org.get('email')
                })
        
        # Контрагенты (для email)
        response = session.get(
            'https://api.moysklad.ru/api/remap/1.2/entity/counterparty',
            headers=headers, verify=False, timeout=60
        )
        
        if response.status_code == 200:
            for cp in response.json().get('rows', []):
                if supplier and cp.get('name') == supplier.name:
                    supplier_email = cp.get('email', '')
                    break
    
    if not supplier_email and supplier:
        supplier_email = supplier.email or ''
    
    # Сотрудники для копий
    from app.models.user import User
    employees = User.query.filter_by(is_active=True).all()
    
    return render_template(
        'orders_supplier/send.html',
        order=order,
        supplier=supplier,
        organizations=organizations,
        employees=employees,
        supplier_email=supplier_email
    )

@orders_supplier_bp.route('/orders-supplier/order/<int:order_id>/send-submit', methods=['POST'])
@login_required
def send_order_submit(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Данные из формы
    to_email = request.form.get('to_email', '')
    subject = request.form.get('subject', '')
    message_text = request.form.get('message', '')
    confirmation_link = request.form.get('confirmation_link', '')
    
    # Получатели
    to_emails = [to_email] if to_email else []
    cc_index = 0
    while True:
        cc = request.form.get('cc_' + str(cc_index))
        if cc is None:
            break
        if cc:
            to_emails.append(cc)
        cc_index += 1
    
    # Тело письма
    confirmation_url = 'https://luna888.ru/confirm/' + confirmation_link
    
    # HTML тело письма
    html_body = '''<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: #0f3460; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center;">
        <h2 style="margin: 0;">🌙 LUNA888</h2>
    </div>
    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #dee2e6;">
        <p style="font-size: 16px; color: #333;">''' + message_text + '''</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="''' + confirmation_url + '''" style="background: #0f3460; color: white; padding: 15px 40px; border-radius: 25px; text-decoration: none; font-size: 16px; font-weight: bold; display: inline-block;">✅ Подтвердить заказ</a>
        </div>
        
        <div style="border-top: 2px solid #0f3460; margin-top: 30px; padding-top: 20px; color: #666; font-size: 14px;">
            <strong>С уважением,</strong><br>
            ''' + (current_user.full_name or current_user.email) + '''<br>
            ''' + current_user.email + '''<br>
            ''' + (current_user.phone or '') + '''
        </div>
    </div>
</body>
</html>'''
    
    body = html_body
    
    # Отправка письма
    # Формируем данные для Excel
    items_data = []
    for item in order.items:
        product = item.product
        if product:
            items_data.append({
                'article': product.article,
                'size': product.size,
                'barcode': product.barcode,
                'quantity': item.quantity
            })
    
    from app.services.send_email import send_email_html
    result = send_email_html(to_emails, subject, body, order, items_data=items_data)
    
    if 'error' in result:
        flash('Ошибка отправки: ' + result['error'], 'error')
        return redirect(url_for('orders_supplier.send_order', order_id=order.id))
    
    order.is_sent = True
    db.session.commit()
    
    flash('Письмо отправлено', 'success')
    return redirect(url_for('orders_supplier.index'))

@orders_supplier_bp.route('/orders-supplier/api/next-number')
@login_required
def api_next_number():
    today = datetime.now().strftime('%d.%m.%Y')
    total_orders = Order.query.count()
    
    next_number = None
    for i in range(1, total_orders + 2):
        candidate = f"{i:02d}-{today}"
        exists = Order.query.filter_by(order_number=candidate).first()
        if not exists:
            next_number = candidate
            break
    
    if not next_number:
        next_number = f"{total_orders + 1:02d}-{today}"
    
    return jsonify({'next_number': next_number})

@orders_supplier_bp.route('/orders-supplier/api/last-settings')
@login_required
def api_last_settings():
    settings = OrderSettings.query.order_by(OrderSettings.id.desc()).first()
    
    if not settings:
        return jsonify({'min_stock': 3, 'delivery_days': 7, 'period': '30'})
    
    return jsonify(settings.to_dict())

@orders_supplier_bp.route('/orders-supplier/api/days-on-shelf')
@login_required
def api_days_on_shelf():
    import requests as req
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    token = get_setting('moysklad_token')
    if not token:
        return jsonify({'error': 'Токен не указан'})
    
    session = req.Session()
    session.trust_env = False
    session.proxies = {'http': None, 'https': None}
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json;charset=utf-8"}
    
    response = session.get(
        'https://api.moysklad.ru/api/remap/1.2/entity/supply',
        headers=headers, verify=False, timeout=60
    )
    
    if response.status_code != 200:
        return jsonify({'error': 'Ошибка API'})
    
    supplies = response.json().get('rows', [])
    supplies.sort(key=lambda x: x.get('moment', ''), reverse=True)
    
    days_map = {}
    
    for supply in supplies:
        supply_date = supply.get('moment', '')[:10]
        
        pos_resp = session.get(
            f"https://api.moysklad.ru/api/remap/1.2/entity/supply/{supply.get('id')}/positions",
            headers=headers, params={'limit': 1000}, verify=False, timeout=60
        )
        
        if pos_resp.status_code == 200:
            for p in pos_resp.json().get('rows', []):
                v_href = p.get('assortment', {}).get('meta', {}).get('href', '')
                v_id = v_href.split('/')[-1] if v_href else ''
                
                if v_id and v_id not in days_map:
                    days_map[v_id] = supply_date
    
    return jsonify({'days_map': days_map})

@orders_supplier_bp.route('/orders-supplier/api/suppliers')
@login_required
def api_suppliers():
    suppliers = Supplier.query.filter_by(is_active=True).all()
    return jsonify({'suppliers': [s.to_dict() for s in suppliers]})

@orders_supplier_bp.route('/orders-supplier/api/supplier/add', methods=['POST'])
@login_required
def api_add_supplier():
    data = request.json
    
    supplier = Supplier(
        name=data.get('name', ''),
        full_name=data.get('full_name', ''),
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        actual_address=data.get('actual_address', ''),
        legal_address=data.get('legal_address', ''),
        inn=data.get('inn', ''),
        kpp=data.get('kpp', ''),
        ogrn=data.get('ogrn', ''),
        okpo=data.get('okpo', ''),
        comment=data.get('comment', ''),
        director_name=data.get('director_name', ''),
        director_position=data.get('director_position', '')
    )
    
    db.session.add(supplier)
    db.session.commit()
    
    return jsonify({'success': True, 'id': supplier.id})

@orders_supplier_bp.route('/orders-supplier/api/supplier/<int:supplier_id>', methods=['PUT', 'DELETE'])
@login_required
def api_edit_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    
    if request.method == 'DELETE':
        supplier.is_active = False
        db.session.commit()
        return jsonify({'success': True})
    
    data = request.json
    supplier.name = data.get('name', supplier.name)
    supplier.phone = data.get('phone', supplier.phone)
    supplier.email = data.get('email', supplier.email)
    supplier.comment = data.get('comment', supplier.comment)
    db.session.commit()
    
    return jsonify({'success': True})

@orders_supplier_bp.route('/orders-supplier/api/orders')
@login_required
def api_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify({'orders': [o.to_dict() for o in orders]})

@orders_supplier_bp.route('/orders-supplier/api/order/<int:order_id>/data')
@login_required
def api_order_data(order_id):
    order = Order.query.get_or_404(order_id)
    
    items = []
    for item in order.items:
        product = item.product
        items.append({
            'product_id': item.product_id,
            'article': product.article if product else '',
            'size': product.size if product else '',
            'quantity': item.quantity
        })
    
    return jsonify({
        'order': order.to_dict(),
        'supplier_id': order.supplier_id,
        'min_stock': order.min_stock,
        'delivery_days': order.delivery_days,
        'sales_period': order.sales_period,
        'items': items
    })

@orders_supplier_bp.route('/orders-supplier/api/order/create', methods=['POST'])
@login_required
def api_create_order():
    data = request.json
    supplier_id = data.get('supplier_id')
    
    today = datetime.now().strftime('%d.%m.%Y')
    total_orders = Order.query.count()
    
    order_number = None
    for i in range(total_orders + 2):
        candidate = f"{i+1:02d}-{today}"
        exists = Order.query.filter_by(order_number=candidate).first()
        if not exists:
            order_number = candidate
            break
    
    if not order_number:
        order_number = f"{total_orders + 1:02d}-{today}"
    
    confirmation_link = secrets.token_urlsafe(32)
    
    order = Order(
        order_number=order_number,
        supplier_id=supplier_id,
        status='pending',
        confirmation_link=confirmation_link,
        min_stock=data.get('min_stock', 3),
        delivery_days=data.get('delivery_days', 7),
        sales_period=data.get('sales_period', '30')
    )
    db.session.add(order)
    db.session.commit()
    
    items = data.get('items', [])
    for item in items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.get('product_id'),
            quantity=item.get('quantity', 0)
        )
        db.session.add(order_item)
    
    db.session.commit()
    
    # Сохраняем настройки
    order_settings = OrderSettings(
        min_stock=data.get('min_stock', 3),
        delivery_days=data.get('delivery_days', 7),
        sales_period=data.get('sales_period', '30'),
        supplier_id=supplier_id
    )
    db.session.add(order_settings)
    db.session.commit()
    
    return jsonify({'success': True, 'order': order.to_dict()})

@orders_supplier_bp.route('/orders-supplier/api/order/<int:order_id>/update', methods=['PUT'])
@login_required
def api_update_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.status == 'confirmed':
        return jsonify({'error': 'Подтверждённый заказ нельзя редактировать'}), 400
    
    data = request.json
    
    if data.get('supplier_id'):
        order.supplier_id = data.get('supplier_id')
    
    order.min_stock = data.get('min_stock', order.min_stock)
    order.delivery_days = data.get('delivery_days', order.delivery_days)
    order.sales_period = data.get('sales_period', order.sales_period)
    
    db.session.commit()
    
    items = data.get('items', [])
    OrderItem.query.filter_by(order_id=order.id).delete()
    
    for item in items:
        if item.get('quantity', 0) > 0:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.get('product_id'),
                quantity=item.get('quantity', 0)
            )
            db.session.add(order_item)
    
    db.session.commit()
    
    return jsonify({'success': True, 'order': order.to_dict()})

@orders_supplier_bp.route('/orders-supplier/api/order/<int:order_id>/delete', methods=['DELETE'])
@login_required
def api_delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.status == 'confirmed':
        return jsonify({'error': 'Подтверждённый заказ нельзя удалить'}), 400
    
    db.session.delete(order)
    db.session.commit()
    
    return jsonify({'success': True})

# Подтверждение заказа
@orders_supplier_bp.route('/confirm/<link>')
def confirm_order(link):
    order = Order.query.filter_by(confirmation_link=link).first()
    if not order:
        return render_template('orders_supplier/confirm_error.html')
    return render_template('orders_supplier/confirm.html', order=order)

@orders_supplier_bp.route('/confirm/<link>/submit', methods=['POST'])
def submit_confirm(link):
    order = Order.query.filter_by(confirmation_link=link).first()
    if not order:
        return jsonify({'error': 'Заказ не найден'}), 404
    
    delivery_date = request.form.get('delivery_date')
    order.status = 'confirmed'
    order.delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d')
    order.confirmation_link = None
    db.session.commit()
    
    return render_template('orders_supplier/confirm_success.html', order=order)
