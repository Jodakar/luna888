from flask import Blueprint, render_template
from flask_login import login_required

orders_mp_bp = Blueprint('orders_mp', __name__)

@orders_mp_bp.route('/orders_mp')
@login_required
def index():
    return render_template('orders_mp/index.html')
