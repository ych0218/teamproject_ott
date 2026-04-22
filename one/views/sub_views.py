from flask import Blueprint, redirect, render_template, url_for

bp=Blueprint('sub',__name__,url_prefix='/')

@bp.route('/sub')
def index():
    return render_template('sub/sub.html')