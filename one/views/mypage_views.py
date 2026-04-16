from flask import Blueprint, redirect, url_for, render_template, session, request, flash
from datetime import datetime
from werkzeug.security import generate_password_hash
from one.filters  import format_datetime

from one.models import User
from one import db

bp = Blueprint('mypage', __name__, url_prefix='/mypage')

@bp.route('/main')
def mypage():
    # 1. 세션에 값이 없으면 테스트용으로 1을 먼저 부여합니다.
    # if not session.get('user_unique_id'):
    session['user_unique_id'] = 4
        # Flask-Login을 사용 중이라면 아래 줄도 추가해야 @login_required가 작동합니다.
        # login_user(User.query.get(1))

    # 2. 세션에서 ID를 가져옵니다.
    user_unique_id = session.get('user_unique_id')

    # 3. DB에서 유저 정보를 조회합니다.
    # user_unique_id가 PK가 맞는지 꼭 확인하세요!
    user_data = User.query.get_or_404(user_unique_id)

    # 4. 템플릿으로 데이터 전달
    return render_template('mypage/mypage_main.html', user=user_data)

@bp.route('/change')
# @login_required
def change_info():

    # 1. 세션에서 user_unique_id 가져오기
    # 1. 마이페이지와 동일하게 유저 조회 (고정값 1 사용 중이시니 동일하게 적용)
    user_unique_id = session.get('user_unique_id')
    user_data = User.query.get_or_404(user_unique_id)

    if request.method == 'POST':
        # 폼 데이터 가져오기
        # --- [수정 실행 로직] ---
        new_name = request.form.get('user_name')
        new_birth = request.form.get('user_birth')
        new_phone = request.form.get('user_phone')
        new_password = request.form.get('user_password')

        # 1. 일반 정보 업데이트
        user_data.user_name = new_name
        user_data.user_phone = new_phone

        # 날짜 문자열 처리 (YYYY-MM-DD 형식으로 들어올 경우)
        if new_birth:
            try:
                # HTML date input은 'YYYY-MM-DD' 형식으로 들어옵니다.
                user_data.user_birth = datetime.strptime(new_birth, '%Y-%m-%d')
            except ValueError:
                flash("날짜 형식이 올바르지 않습니다.", "danger")

        # 2. 비밀번호 변경 (입력값이 있을 경우에만)
        if new_password:
            user_data.user_password = generate_password_hash(new_password)

        try:
            db.session.commit()
            flash('회원 정보가 성공적으로 수정되었습니다.', 'success')
            return redirect(url_for('mypage.mypage'))
        except Exception as e:
            db.session.rollback()
            flash('수정 중 오류가 발생했습니다.', 'danger')


        # --- [페이지 이동 로직] ---
        # 유저 정보를 'user' 변수로 넘겨서 input 태그에 뿌려줄 수 있게 함
    return render_template('mypage/mypage_change.html', user=user_data)


@bp.route('/support')
def support():
    # 유저정보 가지고 가야됨
    # 1. 세션에서 로그인한 유저의 고유 ID(PK)를 가져옵니다.
    # 로그인 시 session['user_unique_id'] = user.user_unique_id 처럼 저장했다고 가정합니다.
    # user_unique_id = session.get('user_unique_id')
    user_unique_id = 1
    # 2. 로그인이 안 되어 있다면 로그인 페이지로 보냅니다.
    # if not user_unique_id:
    #     return redirect(url_for('auth.login'))  # 'auth.login'은 실제 로그인 경로 함수명

    # 3. DB에서 유저 정보를 조회합니다.
    # 작성하신 users 테이블의 프라이머리 키인 user_unique_id로 검색합니다.
    user_data = User.query.get_or_404(user_unique_id)

    # 4. 조회된 유저 객체를 'user'라는 이름으로 HTML에 넘겨줍니다.
    return render_template('mypage/support.html', user=user_data)

@bp.route('/subscription')
def subscription():
    # 유저정보 가지고 가야됨
    # 1. 세션에서 로그인한 유저의 고유 ID(PK)를 가져옵니다.
    # 로그인 시 session['user_unique_id'] = user.user_unique_id 처럼 저장했다고 가정합니다.
    # user_unique_id = session.get('user_unique_id')
    user_unique_id = 1
    # 2. 로그인이 안 되어 있다면 로그인 페이지로 보냅니다.
    # if not user_unique_id:
    #     return redirect(url_for('auth.login'))  # 'auth.login'은 실제 로그인 경로 함수명

    # 3. DB에서 유저 정보를 조회합니다.
    # 작성하신 users 테이블의 프라이머리 키인 user_unique_id로 검색합니다.
    user_data = User.query.get_or_404(user_unique_id)

    # 4. 조회된 유저 객체를 'user'라는 이름으로 HTML에 넘겨줍니다.
    return render_template('mypage/subscription.html', user=user_data)