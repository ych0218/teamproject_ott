from flask import Blueprint, render_template

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
def admin_main():
    return render_template('admin/admin_main.html')