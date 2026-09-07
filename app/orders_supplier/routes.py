from flask import Blueprint, render_template
from flask_login import login_required

orders_supplier_bp = Blueprint('orders_supplier', __name__)

@orders_supplier_bp.route('/orders-supplier')
@login_required
def index():
    return render_template('orders_supplier/index.html')
