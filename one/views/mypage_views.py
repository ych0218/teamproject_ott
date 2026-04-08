from flask import Blueprint, redirect, url_for, render_template

bp = Blueprint('test', __name__, url_prefix='/')

@bp.route('/mypage')
def mypage():
    return render_template('mypage/mypage.html')
