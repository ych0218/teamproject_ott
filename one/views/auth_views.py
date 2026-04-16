from flask import Blueprint, session, render_template, redirect, request, flash, url_for
from one.forms import LoginForm, UserCreateForm, FindIdForm, ResetPasswordForm
from datetime import datetime
from functools import wraps
from one.models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import urllib.parse

bp = Blueprint('auth', __name__, url_prefix='/')

NAVER_CLIENT_ID = "lcxQzP8cM2q3js42vNfp"
NAVER_CLIENT_SECRET = "sGNLiu_pnW"
NAVER_REDIRECT_URI = "http://127.0.0.1:5000/auth/naver/callback"

KAKAO_CLIENT_ID = "84dc069e3a8f7c1f8b250fd44aee633b"
REDIRECT_URI = "http://127.0.0.1:5000/auth/kakao/callback"


@bp.route('/auth/naver/login')
def naver_login():
    state = "1234"

    url = "https://nid.naver.com/oauth2.0/authorize?" + urllib.parse.urlencode({
        "response_type": "code",
        "client_id": NAVER_CLIENT_ID,
        "redirect_uri": NAVER_REDIRECT_URI,
        "state": state
    })

    return redirect(url)


@bp.route('/auth/naver/callback')
def naver_callback():
    code = request.args.get('code')
    state = request.args.get('state')

    token_res = requests.get("https://nid.naver.com/oauth2.0/token", params={
        "grant_type": "authorization_code",
        "client_id": NAVER_CLIENT_ID,
        "client_secret": NAVER_CLIENT_SECRET,
        "code": code,
        "state": state
    })

    access_token = token_res.json().get("access_token")

    user_res = requests.get(
        "https://openapi.naver.com/v1/nid/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    user_json = user_res.json()
    print("네이버 유저:", user_json)

    response = user_json.get("response", {})
    email = response.get("email")
    naver_id = response.get("id")

    if not email:
        return "이메일 못 받아옴"

    user = User.query.filter_by(user_email=email).first()

    if not user:
        user = User(
            user_email=email,
            user_password="",
            user_name=email,
            signup_method='naver'
        )
        db.session.add(user)
    else:
        user.signup_method = 'naver'

    db.session.commit()

    session['user'] = user.user_unique_id
    return redirect(url_for('home.home'))


@bp.route('/auth/kakao/login')
def kakao_login():
    url = f"https://kauth.kakao.com/oauth/authorize?client_id={KAKAO_CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=account_email"
    return redirect(url)


@bp.route('/auth/kakao/callback')
def kakao_callback():
    code = request.args.get('code')

    token_url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    token_res = requests.post(token_url, data=data)
    token_json = token_res.json()

    print("토큰 응답:", token_json)

    access_token = token_json.get("access_token")

    if not access_token:
        return "토큰 못 받아옴"

    user_url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_res = requests.get(user_url, headers=headers)

    user_json = user_res.json()
    print(user_json)

    email = user_json.get("kakao_account", {}).get("email")
    kakao_id = str(user_json.get("id"))

    if not email:
        print("❌ 이메일 못 받아옴")
        return "이메일 못 받아옴"

    print("카카오 이메일:", email)

    user = User.query.filter_by(user_email=email).first()

    if not user:
        user = User(
            user_email=email,
            user_password="",
            signup_method='kakao',
            kakao_id=kakao_id
        )
        db.session.add(user)
    else:
        user.signup_method = 'kakao'
        user.kakao_id = kakao_id

    db.session.commit()

    if not user.user_active:
        flash("이 계정은 이용이 제한되었습니다.")
        return redirect(url_for('auth.login'))

    session['user'] = user.user_unique_id
    session['kakao_token'] = access_token

    return redirect(url_for('home.index'))


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
            # 생년월일 생성
            birth = datetime(
                int(form.birth_year.data),
                int(form.birth_month.data),
                int(form.birth_day.data)
            )

            # 비밀번호 암호화
            hashed_pw = generate_password_hash(form.password1.data)

            user = User(
                user_email=form.email.data,
                user_password=hashed_pw,
                user_name=form.name.data,
                user_phone=form.phone.data,
                user_gender=form.gender.data,
                user_birth=birth
            )

            db.session.add(user)
            db.session.commit()

            flash("회원가입 완료!")
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            print(e)
            flash("서버 오류가 발생했습니다.")

        # try 밖에 있어야 함
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
            return redirect(url_for('home.main'))
        else:
            flash("이메일 또는 비밀번호가 틀렸습니다.")

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    access_token = session.get('kakao_token')

    if access_token:
        requests.post(
            "https://kapi.kakao.com/v1/user/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    session.clear()
    flash("로그아웃 되었습니다.")
    return redirect(url_for('home.index'))


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
                return redirect(url_for('main.index'))
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

    if request.method == 'POST':
        print("form errors:", form.errors)
        print("validate:", form.validate())

    if form.validate_on_submit():
        user = User.query.filter_by(
            user_email=form.email.data,
            user_name=form.name.data
        ).first()

        if user:
            user.user_password = generate_password_hash(form.password1.data)
            db.session.commit()

            flash("비밀번호가 변경되었습니다!")
            return redirect(url_for('auth.login'))
        else:
            flash("일치하는 계정이 없습니다.")

    return render_template('auth/reset_password.html', form=form)
