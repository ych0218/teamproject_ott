from flask import Blueprint, session, render_template, redirect, request, flash, url_for
from one.forms import LoginForm, UserCreateForm, FindIdForm, ResetPasswordForm
from datetime import datetime
from functools import wraps
from one.models import User, db
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/')


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserCreateForm()

    if request.method == 'POST':
        print("🔥🔥🔥 signup 함수 실행됨")
        print("form data:", request.form)
        print("password1:", request.form.get('password1'))
        print("password2:", request.form.get('password2'))
        print("errors:", form.errors)

        print("validate_on_submit:", form.validate_on_submit())
        print("validate:", form.validate())

    if form.validate_on_submit():
        try:
            # 데이터 가져오기
            email = form.email.data
            password = form.password1.data
            name = form.name.data
            phone = form.phone.data
            gender = form.gender.data

            year = form.birth_year.data
            month = form.birth_month.data
            day = form.birth_day.data

            # 생년월일 생성
            birth = None
            if year and month and day:
                birth = datetime(int(year), int(month), int(day))

            # 비밀번호 암호화
            hashed_pw = generate_password_hash(password)

            # 유저 생성
            user = User(
                user_id=email,
                user_password=hashed_pw,
                user_email=email,
                user_name=name,
                user_phone=phone,
                user_gender=gender,
                user_birth=birth
            )

            # DB 저장
            db.session.add(user)
            db.session.commit()

            flash("회원가입 완료!")
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            print(e)
            flash("회원가입 실패")

    return render_template('auth/signup.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(user_email=email).first()

        if user and check_password_hash(user.user_password, password):

            if not user.user_active:
                flash("이 계정은 이용이 제한되었습니다.")
                return redirect(url_for('auth.login'))

            session['user'] = user.user_unique_id
            flash("로그인 성공!")
            return redirect(url_for('home.index'))
        else:
            flash("이메일 또는 비밀번호가 틀렸습니다.")

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

@bp.route('/find-id', methods=['GET', 'POST'])
def find_id():
    form = FindIdForm()

    if form.validate_on_submit():
        user = User.query.filter_by(
            user_name=form.name.data,
            user_phone=form.phone.data
        ).first()

        if user:
            flash(f"회원님의 이메일은 {user.user_email} 입니다.")
        else:
            flash("일치하는 계정이 없습니다.")

    return render_template('auth/find_id.html', form=form)

@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(
            user_email=form.email.data,
            user_id=form.user_id.data
        ).first()

        if user:
            user.user_password = generate_password_hash(form.password1.data)
            db.session.commit()

            flash("비밀번호가 변경되었습니다!")
            return redirect(url_for('auth.login'))
        else:
            flash("일치하는 계정이 없습니다.")

    return render_template('auth/reset_password.html', form=form)