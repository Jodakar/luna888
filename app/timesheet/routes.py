from flask import Blueprint, render_template
from flask_login import login_required

timesheet_bp = Blueprint('timesheet', __name__)

@timesheet_bp.route('/timesheet')
@login_required
def index():
    return render_template('timesheet/index.html')
