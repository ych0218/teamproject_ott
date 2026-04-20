from time import timezone
import requests
import os
from flask import Blueprint, redirect, url_for, render_template, session, request, flash, get_flashed_messages, \
    current_app, jsonify
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import json # 상단에 추가
from one.models import User, Support, SupportAnswer, Plan, Subscription, Payment, Notice
from one import db
import base64  # 토스 API 인증용



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
def change_info():
    user_unique_id = session.get('user')
    user_data = User.query.get_or_404(user_unique_id)

    # --- [GET 요청 처리: 페이지 분기] ---
    if request.method == 'GET':
        # 소셜 유저(kakao, naver)이면서 이름이나 전화번호가 없는 경우 -> 통합 페이지로
        if user_data.signup_method in ['naver', 'kakao']:
            if not user_data.user_password or not user_data.user_name or not user_data.user_phone:
                return render_template('mypage/mypage_integrate.html', user=user_data)

        # 그 외(일반 유저 또는 이미 정보를 입력한 소셜 유저) -> 일반 수정 페이지로
        return render_template('mypage/mypage_change.html', user=user_data)

    # --- [POST 요청 처리: 데이터 저장] ---
    if request.method == 'POST':
        current_pw_input = request.form.get('current_password')
        new_pw = request.form.get('user_password')
        confirm_pw = request.form.get('confirm_password')

        # 1. 가입 방식에 따른 비밀번호 검증 분기
        # 💡 [보안 강화] 소셜 유저라도 이미 비밀번호를 설정했다면 검증을 거쳐야 합니다.
        # 즉, 비밀번호가 DB에 존재(통합 완료)하는 유저만 현재 비밀번호 확인을 실행합니다.
        if user_data.user_password:
            if not current_pw_input or not check_password_hash(user_data.user_password, current_pw_input):
                flash('현재 비밀번호가 일치하지 않습니다.', 'danger')
                return redirect(url_for('mypage.change_info'))
        else:
            print(f"🔗 미통합 소셜유저({user_data.signup_method}) 첫 비밀번호 설정 진행")
            # 소셜 유저는 현재 비밀번호가 없으므로 통과 (로그 확인용)
            print(f"🔗 소셜유저({user_data.signup_method}) 통합/수정 진행")

        # 2. 새 비밀번호 등록/변경 로직
        if new_pw:
            if new_pw == user_data.user_email:
                flash('비밀번호는 이메일 주소와 동일할 수 없습니다.', 'danger')
                return redirect(url_for('mypage.change_info'))
            if new_pw != confirm_pw:
                flash('새 비밀번호가 일치하지 않습니다.', 'danger')
                return redirect(url_for('mypage.change_info'))

            # 해싱하여 저장
            user_data.user_password = generate_password_hash(new_pw)

        # 3. 사용자 정보 업데이트
        user_data.user_name = request.form.get('user_name')
        user_data.user_phone = request.form.get('user_phone')

        raw_birth = request.form.get('user_birth')
        if raw_birth:
            try:
                user_data.user_birth = datetime.strptime(raw_birth, '%Y-%m-%d')
            except:
                pass

        try:
            db.session.commit()
            flash('회원 정보가 성공적으로 반영되었습니다.', 'success')
            return redirect(url_for('mypage.mypage'))
        except Exception as e:
            db.session.rollback()
            print(f"❌ DB 저장 에러: {e}")
            flash('저장 중 오류가 발생했습니다.', 'danger')
            return redirect(url_for('mypage.change_info'))

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


@bp.route('/support-center')
def support_center():
    user_unique_id = session.get('user')

    if not user_unique_id:
        return redirect(url_for('auth.login'))

    user_data = User.query.get_or_404(user_unique_id)

    # 1. 내 문의 내역 조회
    my_supports = Support.query.filter_by(user_unique_id=user_unique_id) \
        .order_by(Support.created_at.desc()).all()

    # 2. 공지사항 조회 (고정글 우선 -> 최신순 정렬)
    # .desc()를 사용하면 True(1)가 False(0)보다 먼저 나옵니다.
    notices = Notice.query.order_by(Notice.is_pinned.desc(), Notice.created_at.desc()).all()

    return render_template('mypage/support_center.html',
                           user=user_data,
                           supports=my_supports,
                           notices=notices) # notices 추가


@bp.route('/notice/<int:notice_id>')
def notice_detail(notice_id):
    # DB에서 해당 공지사항 조회
    notice = Notice.query.get_or_404(notice_id)

    # 조회수 증가 (선택 사항)
    notice.view_count += 1
    db.session.commit()

    return render_template('mypage/notice_detail.html', notice=notice)



@bp.route('/support-center/write', methods=['POST'])
def support_center_write():
    user_id = session.get('user')
    if not user_id:
        return redirect(url_for('auth.login'))

    # 1. 데이터 및 파일 수집
    category = request.form.get('category')
    title = request.form.get('title')
    content = request.form.get('content')
    image_file = request.files.get('support_img')

    saved_file_path = None

    # 2. 이미지 저장 로직 (기존 로직 활용)
    if image_file and image_file.filename != '':
        filename = secure_filename(image_file.filename)
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        upload_folder = os.path.join(current_app.root_path, 'static', 'img', 'support')

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        image_file.save(os.path.join(upload_folder, unique_filename))
        saved_file_path = f"img/support/{unique_filename}"

    # 3. DB 저장
    new_support = Support(
        user_unique_id=user_id,
        category=category,
        title=title,
        content=content,
        image_url=saved_file_path,
        status='pending',
        created_at=datetime.now(timezone.utc)
    )

    try:
        db.session.add(new_support)
        db.session.commit()

        # 💡 [핵심] 성공 후 다시 고객센터 페이지를 렌더링하며 success 플래그 전달
        user_data = User.query.get(user_id)
        supports = Support.query.filter_by(user_unique_id=user_id).all()

        # 문의 등록 성공 시 'success' 변수를 들고 고객센터 메인으로 갑니다.
        return render_template('mypage/support_center.html',
                               user=user_data,
                               supports=supports,
                               success=True)
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return "처리 중 오류 발생", 500






@bp.route('/subscribe')
def subscribe():
    user_id = session.get('user')
    now = datetime.now()

    # ⏳ [상태 자동 업데이트] 만료시간 지났는데 아직 active인 것들 찾기
    overdue_subs = Subscription.query.filter(
        Subscription.user_unique_id == user_id,
        Subscription.status == 'active',
        Subscription.end_date < now
    ).all()

    for sub in overdue_subs:
        sub.status = 'expired'

    if overdue_subs:
        db.session.commit()

    # (이후 기존 로직...)
    user_data = User.query.get_or_404(user_id)
    plans = Plan.query.order_by(Plan.price).all()
    active_sub = Subscription.query.filter_by(user_unique_id=user_id, status='active').first()

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
            status='결제완료',
            paid_at=now
        )
        db.session.add(new_payment)
        db.session.commit()

        flash("결제가 완료되었습니다!")
        return redirect(url_for('mypage.mypage'))

    except Exception as e:
        db.session.rollback()
        return redirect(url_for('mypage.subscribe'))

TOSS_SECRET_KEY = "test_sk_GePWvyJnrKRbowbdn5jqVgLzN97E"


@bp.route('/payment/success')
def payment_success():
    payment_key = request.args.get('paymentKey')
    order_id = request.args.get('orderId')
    amount = request.args.get('amount')
    plan_id = request.args.get('planId')

    user_unique_id = session.get('user')
    if not user_unique_id:
        return redirect(url_for('auth.login'))
    print(f"Secret Key: {TOSS_SECRET_KEY[:10]}...")
    # 1. 토스 승인 API 호출 (인증 및 최종 승인)
    secret_key_raw = TOSS_SECRET_KEY + ":"
    encoded_key = base64.b64encode(secret_key_raw.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "paymentKey": payment_key,
        "orderId": order_id,
        "amount": int(amount)
    }

    url = "https://api.tosspayments.com/v1/payments/confirm"
    res = requests.post(url, json=payload, headers=headers)

    if res.status_code == 200:
        # --- [DB 작업 시작] ---
        try:
            plan_id = request.args.get('planId')
            amount = request.args.get('amount')
            plan = Plan.query.get_or_404(plan_id)
            now = datetime.now()

            # 1. 이용 기간 계산 (개월 수 대응)
            duration_map = {'starter': 1, 'basic': 3, 'standard': 6, 'premium': 12}
            add_days = 30 * duration_map.get(plan.plan_name.lower(), 1)

            # 2. 연장 대상 찾기 (상태가 active이고 아직 만료 전인 구독)
            active_sub = Subscription.query.filter(
                Subscription.user_unique_id == session.get('user'),
                Subscription.status == 'active',
                Subscription.end_date > now
            ).first()

            if active_sub:
                # 🔄 [기존 구독 연장]
                active_sub.end_date += timedelta(days=add_days)
                active_sub.plan_id = plan.plan_id  # 요금제 변경 시 업데이트
                target_sub = active_sub
            else:
                # ✨ [신규 구독 생성] (처음이거나 이미 만료된 경우)
                target_sub = Subscription(
                    user_unique_id=session.get('user'),
                    plan_id=plan.plan_id,
                    start_date=now,
                    end_date=now + timedelta(days=add_days),
                    status='active'
                )
                db.session.add(target_sub)
                db.session.flush()

            # 3. 결제 내역 저장
            new_payment = Payment(
                user_unique_id=session.get('user'),
                subscription_id=target_sub.subscription_id,
                price=amount,
                status='결제완료',
                paid_at=now
            )
            db.session.add(new_payment)
            db.session.commit()
            session['show_payment_modal'] = {
                'plan': plan.plan_name.upper(),
                'amount': "{:,.0f}".format(int(amount)),
                'end_date': target_sub.end_date.strftime('%Y-%m-%d')
            }
            flash(f"{plan.plan_name.upper()} 이용권 결제가 완료되었습니다!")
            return redirect(url_for('mypage.mypage'))

        except Exception as e:
            db.session.rollback()
            flash("정보 저장 중 오류가 발생했습니다.")
            return redirect(url_for('mypage.subscribe'))
    else:
        print(f"토스 승인 실패: {res.text}")  # 터미널에 찍히는 메시지가 중요합니다!
        flash("결제 승인에 실패했습니다.", "danger")
        return redirect(url_for('mypage.subscribe'))

@bp.route('/payment/fail')
def payment_fail():
    message = request.args.get('message') or "결제 중 오류가 발생했습니다."
    flash(message, "danger")
    return redirect(url_for('mypage.subscribe'))