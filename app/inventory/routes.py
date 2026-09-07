from flask import Blueprint, render_template
from flask_login import login_required

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory')
@login_required
def index():
    return render_template('inventory/index.html')
