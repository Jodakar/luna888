from flask import Blueprint, render_template
from flask_login import login_required

orders_mp_bp = Blueprint('orders_mp', __name__)

@orders_mp_bp.route('/marketplace')
@login_required
def index():
    return render_template('orders_mp/index.html')


@orders_mp_bp.route('/marketplace/api/wb-summary')
@login_required
def wb_summary():
    from app.services.sync_wb import sync_wb_all
    from flask import jsonify
    results = sync_wb_all()
    return jsonify(results)


@orders_mp_bp.route('/marketplace/api/wb-orders')
@login_required
def api_wb_orders():
    from app.models.wb import WBOrder
    from flask import jsonify
    orders = WBOrder.query.order_by(WBOrder.created_at.desc()).limit(500).all()
    return jsonify({'orders': [o.to_dict() for o in orders]})

@orders_mp_bp.route('/marketplace/api/wb-sales')
@login_required
def api_wb_sales():
    from app.models.wb import WBSale
    from flask import jsonify
    sales = WBSale.query.order_by(WBSale.sale_date.desc()).limit(500).all()
    return jsonify({'sales': [s.to_dict() for s in sales]})

@orders_mp_bp.route('/marketplace/api/wb-supplies')
@login_required
def api_wb_supplies():
    from app.models.wb import WBSupply
    from flask import jsonify
    supplies = WBSupply.query.order_by(WBSupply.created_at.desc()).limit(100).all()
    return jsonify({'supplies': [s.to_dict() for s in supplies]})

@orders_mp_bp.route('/marketplace/api/wb-returns')
@login_required
def api_wb_returns():
    from app.models.wb import WBReturn
    from flask import jsonify
    returns = WBReturn.query.order_by(WBReturn.created_at.desc()).limit(500).all()
    return jsonify({'returns': [r.to_dict() for r in returns]})


@orders_mp_bp.route('/marketplace/api/scan')
@login_required
def api_scan():
    from app.models.product import Product
    from flask import jsonify, request
    barcode = request.args.get('barcode', '').strip()
    
    if not barcode:
        return jsonify({'error': 'Пустой баркод'}), 400
    
    # Ищем товар по баркоду
    product = Product.query.filter_by(barcode=barcode).first()
    if not product and len(barcode) == 14 and barcode.startswith('0'):
        product = Product.query.filter_by(barcode=barcode[1:]).first()
    if not product and len(barcode) == 13:
        product = Product.query.filter_by(barcode='0' + barcode).first()
    
    if not product:
        return jsonify({'product': None, 'message': 'Товар не найден'})
    
    return jsonify({'product': product.to_dict()})


@orders_mp_bp.route('/marketplace/api/create-shipping', methods=['POST'])
@login_required
def api_create_shipping():
    from app.services.moysklad_docs import create_demand
    from flask import jsonify, request
    
    data = request.json
    items = data.get('items', [])
    
    result = create_demand(items)
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 400
    
    return jsonify({'success': True, 'demand': result})

@orders_mp_bp.route('/marketplace/api/create-receiving', methods=['POST'])
@login_required
def api_create_receiving():
    from app.services.moysklad_docs import create_supply
    from flask import jsonify, request
    
    data = request.json
    items = data.get('items', [])
    
    result = create_supply(items)
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 400
    
    return jsonify({'success': True, 'supply': result})
