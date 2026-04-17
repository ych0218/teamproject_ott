from time import timezone
import os
from flask import Blueprint, redirect, url_for, render_template, session, request, flash, get_flashed_messages, current_app
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from one.filters  import format_datetime

from one.models import User, Support, SupportAnswer
from one import db

bp = Blueprint('mypage', __name__, url_prefix='/mypage')

@bp.route('/main')
def mypage():
    # 1. 세션에서 로그인한 사용자의 ID를 가져옵니다. ('user' 키 사용)
    user_unique_id = session.get('user')

    # 2. 로그인하지 않은 사용자가 접근했을 경우 처리
    if not user_unique_id:
        flash("로그인이 필요한 서비스입니다.")
        return redirect(url_for('auth.login'))

    # 3. 세션의 ID로 DB에서 유저 정보를 조회합니다.
    # 데이터가 없으면 404 에러를 띄웁니다.
    user_data = User.query.get_or_404(user_unique_id)

    # 4. 템플릿으로 데이터 전달
    return render_template('mypage/mypage_main.html', user=user_data)

@bp.route('/change', methods=['GET', 'POST'])
# @login_required
def change_info():
    get_flashed_messages()
    # 세션에서 user_unique_id 가져오기
    user_unique_id = session.get('user')
    user_data = User.query.get_or_404(user_unique_id)

    if request.method == 'POST':
        # 현재 비밀번호 검증 추가
        current_pw_input = request.form.get('current_password')
        if not check_password_hash(user_data.user_password, current_pw_input):
            flash('현재 비밀번호가 일치하지 않습니다.', 'danger')
            return redirect(url_for('mypage.change_info'))

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


@bp.route('/support/write', methods=['GET', 'POST'])
def support_write():
    user_id = session.get('user')
    if not user_id: return redirect(url_for('auth.login'))

    user_data = User.query.get_or_404(user_id)

    if request.method == 'POST':
        image_file = request.files.get('support_img')
        saved_file_path = None

        if image_file and image_file.filename != '':
            # 1. 파일명 보안 처리 및 중복 방지
            filename = secure_filename(image_file.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"

            # 2. 절대 경로 설정 (이 부분이 중요합니다)
            # static/img/support 폴더를 사용하거나 static/uploads/support를 새로 만듭니다.
            upload_folder = os.path.join(current_app.root_path, 'static', 'img', 'support')

            # 3. 폴더가 없으면 생성
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            # 4. 파일 저장
            image_file.save(os.path.join(upload_folder, unique_filename))

            # 5. DB에 저장할 상대 경로 (static 이후의 경로)
            saved_file_path = f"img/support/{unique_filename}"

        # Support 객체 생성 및 저장
        new_support = Support(
            user_unique_id=user_id,
            category=request.form.get('category'),
            title=request.form.get('title'),
            content=request.form.get('content'),
            image_url=saved_file_path,  # 여기에 경로가 잘 담겨야 합니다.
            status='pending',
            created_at=datetime.now(timezone.utc)
        )

        try:
            db.session.add(new_support)
            db.session.commit()
            return render_template('mypage/support_write.html', user=user_data, success=True)
        except Exception as e:
            db.session.rollback()
            print(f"DB Error: {e}")
            return "저장 중 오류 발생", 500

    return render_template('mypage/support_write.html', user=user_data)
# [문의 상세 보기 - 답변 포함]
@bp.route('/support/detail/<int:support_id>')
def support_detail(support_id):
    user_id = session.get('user')
    # 본인 글인지 확인하는 보안 로직 포함
    support = Support.query.get_or_404(support_id)
    if support.user_unique_id != user_id:
        flash("권한이 없습니다.", "danger")
        return redirect(url_for('mypage.mypage'))

    return render_template('mypage/support_detail.html', support=support)





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