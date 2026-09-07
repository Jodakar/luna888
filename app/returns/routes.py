from flask import Blueprint, render_template
from flask_login import login_required

returns_bp = Blueprint('returns', __name__)

@returns_bp.route('/returns')
@login_required
def index():
    return render_template('returns/index.html')
