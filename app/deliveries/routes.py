from flask import Blueprint, render_template
from flask_login import login_required

deliveries_bp = Blueprint('deliveries', __name__)

@deliveries_bp.route('/deliveries')
@login_required
def index():
    return render_template('deliveries/index.html')
