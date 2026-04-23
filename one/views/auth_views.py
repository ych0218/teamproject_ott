from flask import Blueprint, session, render_template, redirect, request, flash, url_for, jsonify
from one.forms import LoginForm, UserCreateForm, FindIdForm, ResetPasswordForm
from datetime import datetime
from functools import wraps
from one.models import User, db, Admin
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_mail import Mail, Message
# from one import mail
import requests
import urllib.parse
import time
import random


bp = Blueprint('auth', __name__, url_prefix='/')

email_codes = {}


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
    flash("로그인 완료", "success")
    return redirect(url_for('home.main'))


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
        flash("현재 이용할 수 없는 계정입니다.", "error")
        return redirect(url_for('auth.login'))

    session['user'] = user.user_unique_id
    session['kakao_token'] = access_token

    flash("로그인 완료", "success")
    return redirect(url_for('home.main'))


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

            flash("회원가입 완료!", "success")
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

        admin = Admin.query.filter_by(admin_id=email).first()

        if admin and check_password_hash(admin.admin_password, password):
            # 관리자 세션 생성
            session.clear()  # 기존 세션 초기화
            session['admin_user'] = admin.admin_unique_id
            session['admin_name'] = admin.admin_name
            session['is_admin'] = True  # 관리자 여부 플래그
            session['show_admin_login_success'] = True
            return redirect(url_for('admin.admin_main'))  # 관리자 메인 페이지로 이동

        # 2. 관리자가 아니면 일반 유저(User) 테이블 확인
        user = User.query.filter_by(user_email=email).first()

        if user and check_password_hash(user.user_password, password):

            if not user.user_active:
                flash("이 계정은 이용이 제한되었습니다.", "error")
                return redirect(url_for('auth.login'))

            session['user'] = user.user_unique_id
            flash("로그인 완료", "success")
            return redirect(url_for('home.main'))
        # 3. 둘 다 해당하지 않을 경우
        else:
            flash("이메일 또는 비밀번호를 다시 확인해주세요.", "error")

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    # 카카오 로그아웃
    kakao_token = session.get('kakao_token')
    if kakao_token:
        requests.post(
            "https://kapi.kakao.com/v1/user/logout",
            headers={"Authorization": f"Bearer {kakao_token}"}
        )

    # 네이버 로그아웃
    naver_token = session.get('naver_token')
    if naver_token:
        requests.get("https://nid.naver.com/oauth2.0/token", params={
            "grant_type": "delete",
            "client_id": NAVER_CLIENT_ID,
            "client_secret": NAVER_CLIENT_SECRET,
            "access_token": naver_token,
            "service_provider": "NAVER"
        })

    session.clear()
    flash("로그아웃되었습니다.", "success")
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
            flash(user.user_email, "success")
        else:
            flash("NOT_FOUND", "error")

    return render_template('auth/find_id.html', form=form)


@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()

    # ✅ POST(버튼 클릭)일 때만 인증 체크
    if form.validate_on_submit():

        if not session.get('email_verified'):
            flash("이메일 인증이 필요합니다.", "error")
            return render_template('auth/reset_password.html', form=form)

        user = User.query.filter_by(
            user_email=session.get('reset_email'),  # 세션 이메일 사용
            user_name=form.name.data
        ).first()

        if not session.get('reset_email'):
            flash("잘못된 접근입니다.", "error")
            return render_template('auth/reset_password.html', form=form)

        if user:
            user.user_password = generate_password_hash(form.password1.data)
            db.session.commit()

            # ✅ 인증 상태 초기화
            session.pop('email_verified', None)
            session.pop('reset_email', None)

            flash("비밀번호가 변경되었습니다!", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("일치하는 계정이 없습니다.", "error")

    # ✅ GET (페이지 처음 진입)
    return render_template('auth/reset_password.html', form=form)

@bp.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.json
    email = data.get('email')
    code = data.get('code')

    code_data = email_codes.get(email)

    if not code_data:
        return jsonify({'success': False, 'message': '코드 없음'}), 400

    if code_data['code'] != code:
        return jsonify({'success': False, 'message': '코드 불일치'}), 400

    if code_data['expire'] < time.time():
        return jsonify({'success': False, 'message': '코드 만료'}), 400

    # ✅ 인증 성공
    session['email_verified'] = True
    session['reset_email'] = email

    # ✅ 코드 제거
    email_codes.pop(email, None)

    return jsonify({'success': True})


@bp.route('/send-code', methods=['POST'])
def send_code():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({'success': False}), 400

    code = str(random.randint(100000, 999999))

    email_codes[email] = {
        "code": code,
        "expire": time.time() + 300
    }

    # # 🔥 메일 발송
    # msg = Message(
    #     subject="[인증코드] 비밀번호 재설정",
    #     recipients=[email],
    #     body=f"인증코드: {code}\n5분 내에 입력해주세요."
    # )
    #
    # mail.send(msg)

    print("🔥 send-code 들어옴")

    return jsonify({'success': True})