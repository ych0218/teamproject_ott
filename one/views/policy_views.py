from flask import Blueprint, redirect, url_for, render_template

bp = Blueprint('policy', __name__, url_prefix='/policy/')

@bp.route('/terms')
def terms():
    return render_template('policy/term.html')

@bp.route('/pay-terms')
def pay_terms():
    return render_template('policy/pay-term.html')

@bp.route('/email')
def email():
    return render_template('policy/email.html')

@bp.route('/legal')
def legal():
    return render_template('policy/legal.html')

@bp.route('/privacy')
def privacy():
    return render_template('policy/privacy.html')

@bp.route('/youth')
def youth():
    return render_template('policy/youth.html')

