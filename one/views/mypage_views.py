from flask import Blueprint, redirect, url_for, render_template, session

from one.models import User

bp = Blueprint('mypage', __name__, url_prefix='/mypage')

@bp.route('/main')
def mypage():
    # 유저정보 가지고 가야됨
    # 1. 세션에서 로그인한 유저의 고유 ID(PK)를 가져옵니다.
    # 로그인 시 session['user_unique_id'] = user.user_unique_id 처럼 저장했다고 가정합니다.
    user_unique_id = session.get('user_unique_id')

    # 2. 로그인이 안 되어 있다면 로그인 페이지로 보냅니다.
    # if not user_unique_id:
    #     return redirect(url_for('auth.login'))  # 'auth.login'은 실제 로그인 경로 함수명

    # 3. DB에서 유저 정보를 조회합니다.
    # 작성하신 users 테이블의 프라이머리 키인 user_unique_id로 검색합니다.
    user_data = User.query.get_or_404(user_unique_id)

    # 4. 조회된 유저 객체를 'user'라는 이름으로 HTML에 넘겨줍니다.
    return render_template('mypage/mypage_main.html',user=user_data)
