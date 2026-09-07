from flask import Blueprint, render_template
from flask_login import login_required

couriers_bp = Blueprint('couriers', __name__)

@couriers_bp.route('/couriers')
@login_required
def index():
    return render_template('couriers/index.html')
