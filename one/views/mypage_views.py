from flask import Blueprint, redirect, url_for, render_template

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def test():
    return render_template('mypage/test.html')