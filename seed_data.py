from datetime import datetime, date, timezone, timedelta
from one import db, create_app
from one.models import (
    User, Video, Genre, Plan, Admin, Subscription,
    Support, SupportAnswer, WatchHistory, Payment, Notice,
    VideoLike, VideoWish, Review
)

# 1. Flask 앱 인스턴스 생성
app = create_app()


def seed_db():
    with app.app_context():
        print("--- 데이터 삽입 시작 ---")

        # [LAYER 1] 부모 테이블 (FK 참조를 받기만 함)
        # ---------------------------------------------------------
        # 관리자
        admin = Admin(
            admin_id="admin_01",
            admin_password="hashed_admin_password",  # 실서비스 시 암호화 필요
            admin_name="운영자",
            admin_role="superadmin"
        )
        # 장르
        g_action = Genre(genre_name="액션")
        g_sf = Genre(genre_name="SF")
        # 요금제
        plan_p = Plan(plan_name="Premium", price=14500)
        # 사용자
        user = User(
            user_id="testuser_01",
            user_password="hashed_user_password",
            user_email="test@example.com",
            user_name="홍길동",
            user_birth=date(1995, 1, 1),
            user_phone="010-1234-5678",
            user_gender="M"
        )

        db.session.add_all([admin, g_action, g_sf, plan_p, user])
        db.session.flush()  # ID 생성을 위해 메모리상 반영

        # [LAYER 2] 1차 자식 테이블 (LAYER 1의 ID를 참조)
        # ---------------------------------------------------------
        # 영상 (Admin 참조)
        video = Video(
            video_title="인터스텔라",
            video_director="크리스토퍼 놀란",
            video_actor="매튜 맥커너히",
            video_url="https://example.com/interstellar.mp4",
            video_thumbnail="https://example.com/thumb.jpg",
            video_date=date(2014, 11, 6),
            video_age_limit="12세",
            admin_unique_id=admin.admin_unique_id
        )

        # 다대다 관계 (video_genres 연결 테이블 처리)
        video.genres.append(g_sf)
        video.genres.append(g_action)

        # 구독 (User, Plan 참조)
        sub = Subscription(
            user_unique_id=user.user_unique_id,
            plan_id=plan_p.plan_id,
            end_date=datetime.now(timezone.utc) + timedelta(days=30),
            status='active'
        )

        # 공지사항 (Admin 참조)
        notice = Notice(
            admin_unique_id=admin.admin_unique_id,
            title="환영합니다!",
            content="OTT 서비스 오픈 안내입니다.",
            is_pinned=True
        )

        # 고객센터 문의 (User 참조)
        support = Support(
            user_unique_id=user.user_unique_id,
            category="결제문의",
            title="환불 규정이 궁금해요",
            content="구독 취소 시 환불은 어떻게 되나요?",
            status="pending"
        )

        db.session.add_all([video, sub, notice, support])
        db.session.flush()

        # [LAYER 3] 2차 자식 테이블 (LAYER 2의 ID를 참조하거나 복합 관계)
        # ---------------------------------------------------------
        # 시청 기록 (User, Video 참조)
        history = WatchHistory(
            user_unique_id=user.user_unique_id,
            video_unique_id=video.video_unique_id,
            last_played_time=3600,
            is_finished=False
        )

        # 리뷰 (User, Video 참조)
        review = Review(
            user_unique_id=user.user_unique_id,
            video_unique_id=video.video_unique_id,
            comment="최고의 우주 영화!",
            rating=5
        )

        # 결제 (User, Subscription 참조)
        payment = Payment(
            user_unique_id=user.user_unique_id,
            subscription_id=sub.subscription_id,
            price=plan_p.price,
            status="success"
        )

        # 문의 답변 (Support, Admin 참조)
        answer = SupportAnswer(
            support_id=support.support_id,
            admin_unique_id=admin.admin_unique_id,
            content="결제 후 7일 이내 시청 기록이 없을 시 전액 환불 가능합니다."
        )

        # 좋아요 및 찜
        like = VideoLike(user_unique_id=user.user_unique_id, video_unique_id=video.video_unique_id)
        wish = VideoWish(user_unique_id=user.user_unique_id, video_unique_id=video.video_unique_id)

        db.session.add_all([history, review, payment, answer, like, wish])

        # 4. 최종 커밋
        try:
            db.session.commit()
            print("✅ 데이터 삽입 완료! one.db를 확인하세요.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    seed_db()