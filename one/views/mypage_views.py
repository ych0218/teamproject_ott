from time import timezone
import requests
import os
from flask import Blueprint, redirect, url_for, render_template, session, request, flash, get_flashed_messages, \
    current_app, jsonify
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from one.models import User, Support, SupportAnswer, Plan, Subscription, Payment
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








@bp.route('/subscribe')
def subscribe():
    user_unique_id = session.get('user')
    if not user_unique_id:
        return redirect(url_for('auth.login'))

    user_data = User.query.get_or_404(user_unique_id)

    # 모든 요금제 정보 가져오기 (가격순)
    plans = Plan.query.order_by(Plan.price).all()

    # 현재 유저가 이미 사용 중인 활성 구독권이 있는지 확인
    active_sub = Subscription.query.filter_by(
        user_unique_id=user_unique_id,
        status='active'
    ).first()

    return render_template('mypage/subscription.html', user=user_data, plans=plans, active_sub=active_sub)


# [이용권 구매 처리 (POST)]
@bp.route('/purchase/<int:plan_id>', methods=['POST'])
def purchase_plan(plan_id):
    user_unique_id = session.get('user')
    plan = Plan.query.get_or_404(plan_id)

    # 1. 시간 설정 (Naive로 통일)
    now = datetime.now()
    duration_map = {'starter': 1, 'basic': 3, 'standard': 6, 'premium': 12}
    add_days = 30 * duration_map.get(plan.plan_name, 1)

    # 2. 현재 활성 구독 확인
    active_sub = Subscription.query.filter_by(user_unique_id=user_unique_id, status='active').first()

    try:
        # 3. [핵심 수정] 연장하더라도 새로운 구독 레코드를 생성합니다.
        # 기존 구독이 있다면 만료(expired) 처리하여 이력을 보존합니다.
        new_start_date = now
        if active_sub:
            # 기존 종료일이 미래라면 거기서부터 시작, 아니면 지금부터 시작
            current_end = active_sub.end_date.replace(
                tzinfo=None) if active_sub.end_date.tzinfo else active_sub.end_date
            new_start_date = max(current_end, now)
            active_sub.status = 'expired'  # 기존 기록은 과거 요금제 정보를 유지한 채 종료

        # 4. 새로운 구독 생성 (이 시점의 plan_id가 저장됨)
        new_sub = Subscription(
            user_unique_id=user_unique_id,
            plan_id=plan.plan_id,
            start_date=new_start_date,
            end_date=new_start_date + timedelta(days=add_days),
            status='active'
        )
        db.session.add(new_sub)
        db.session.flush()

        # 5. 결제 내역 생성 (새로운 new_sub를 참조하므로 정보가 고정됨)
        new_payment = Payment(
            user_unique_id=user_unique_id,
            subscription_id=new_sub.subscription_id,
            price=plan.price,
            status='success',
            paid_at=now
        )
        db.session.add(new_payment)
        db.session.commit()

        flash("결제가 완료되었습니다!")
        return redirect(url_for('mypage.mypage'))

    except Exception as e:
        db.session.rollback()
        return redirect(url_for('mypage.subscribe'))


@bp.route('/payment/kakao/ready', methods=['POST'])
def kakao_pay_ready():
    user_unique_id = session.get('user')
    if not user_unique_id:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    data = request.get_json()
    plan_id = data.get('plan_id')
    plan_name = data.get('plan_name')
    total_amount = data.get('total_amount')

    # 카카오페이 준비 API 호출
    URL = "https://kakao.com"
    headers = {
        # 내 애플리케이션 > 앱 키 > Admin 키를 입력하세요
        "Authorization": "KakaoAK " + "본인의_ADMIN_KEY_입력",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }

    params = {
        "cid": "TC0ONETIME",  # 테스트용 가맹점 코드
        "partner_order_id": f"order_{user_unique_id}_{plan_id}",  # 주문번호
        "partner_user_id": str(user_unique_id),  # 사용자 ID
        "item_name": f"OTT PASS {plan_name.upper()}",  # 상품명
        "quantity": 1,  # 수량
        "total_amount": total_amount,  # 금액
        "tax_free_amount": 0,  # 비과세 금액
        # 성공/취소/실패 시 돌아올 URL (서버 주소에 맞게 수정)
        "approval_url": f"http://127.0.0{plan_id}",
        "cancel_url": "http://127.0.0",
        "fail_url": "http://127.0.0",
    }

    res = requests.post(URL, headers=headers, params=params)
    result = res.json()

    # 결제 승인 단계에서 사용하기 위해 tid(결제 고유 번호)를 세션에 저장
    session['tid'] = result.get('tid')

    return jsonify(result)


@bp.route('/purchase/kakao/success/<int:plan_id>')
def kakao_pay_success(plan_id):
    pg_token = request.args.get('pg_token')
    tid = session.get('tid')
    user_unique_id = session.get('user')

    # 1. [수정] 카카오페이 승인 API의 정확한 주소
    # 💡 따옴표 안에 키 값만 정확히 들어가야 합니다.
    # 혹시 키 앞뒤로 공백이 있다면 .strip()이 제거해줍니다.
    admin_key = "4690b7854d4e7c725a348cfb9b10025e".strip()

    URL = "https://kakao.com"
    headers = {
        # f-string을 사용하여 'KakaoAK'와 키 사이에 공백 하나만 정확히 들어가게 합니다.
        "Authorization": f"KakaoAK {admin_key}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    # 2. [수정] 결제 준비(Ready) 단계의 partner_order_id와 반드시 일치해야 함
    # 앞서 Ready 단계에서 order_{user_unique_id} 로 보냈다면 여기서도 맞춰야 합니다.
    params = {
        "cid": "TC0ONETIME",
        "tid": tid,
        "partner_order_id": f"order_{user_unique_id}",  # Ready 단계와 동일하게 수정
        "partner_user_id": str(user_unique_id),
        "pg_token": pg_token,
    }

    res = requests.post(URL, headers=headers, params=params)
    res_data = res.json()

    if res.status_code == 200:
        # 3. 결제 성공! 이제 DB에 구독 정보를 저장하는 함수로 보냅니다.
        # 기존에 만드신 'purchase_plan' 함수로 연결하거나 로직을 여기에 작성하세요.
        flash("결제가 성공적으로 완료되었습니다!")
        return redirect(url_for('mypage.purchase_plan', plan_id=plan_id))
    else:
        # 실패 시 에러 로그 확인용
        print(f"Approve Error: {res_data}")
        flash("결제 승인에 실패했습니다.")
        return redirect(url_for('mypage.subscribe'))