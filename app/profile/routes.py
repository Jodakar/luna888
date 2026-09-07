from flask import Blueprint, render_template
from flask_login import login_required

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@login_required
def index():
    return render_template('profile/index.html')
