from flask import Blueprint, redirect, render_template, url_for

bp=Blueprint('sub',__name__,url_prefix='/sub')

@bp.route('/sub')
def sub():
    return render_template('sub/sub.html')