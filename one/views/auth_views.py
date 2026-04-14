from flask import Blueprint, session, render_template, redirect, request, flash, url_for
from one.forms import LoginForm, UserCreateForm
from datetime import datetime
from functools import wraps

bp = Blueprint('auth', __name__, url_prefix='/')


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserCreateForm()
    if form.validate_on_submit():
        # 사용자가 입력한 데이터 가져오기
        email = form.email.data
        password = form.password1.data
        # TODO: 데이터베이스에 사용자 저장 로직 추가 (예: User 모델 생성 및 저장)
        # 가입 완료 후 로그인 페이지로 이동
        return redirect(url_for('auth.login'))
    # 폼 객체를 템플릿에 전달
    return render_template('auth/signup.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # TODO: DB 확인
        session['user'] = email

        return redirect(url_for('main.index'))

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


@bp.route('/adult-check', methods=['GET', 'POST'])
def adult_check():
    if request.method == 'POST':
        birth = request.form.get('birth')

        if birth:
            birth_date = datetime.strptime(birth, "%Y-%m-%d")
            today = datetime.today()

            age = today.year - birth_date.year - (
                    (today.month, today.day) < (birth_date.month, birth_date.day)
            )

            if age >= 19:
                session['is_adult'] = True
                return redirect(url_for('main.index'))  # 원하는 페이지
            else:
                flash('성인만 이용 가능합니다.')

    return render_template('auth/adult_check.html')


def adult_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('is_adult'):
            return redirect(url_for('auth.adult_check'))
        return f(*args, **kwargs)

    return wrapper


@bp.route('/adult-page')
@adult_required
def adult_page():
    return render_template('adult_page.html')



