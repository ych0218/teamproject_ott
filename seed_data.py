from datetime import datetime, date, timezone, timedelta
import random

from one import db, create_app
from one.models import (
    User, Video, Plan, Admin, Subscription,
    Support, SupportAnswer, WatchHistory, Payment, Notice,
    VideoLike, VideoWish, Review
)

# 1. Flask 앱 인스턴스 생성
app = create_app()


def seed_plans():
    # 데이터 리스트 정의
    plan_data = [
        {"plan_name": "starter", "price": 11900},
        {"plan_name": "basic", "price": 32000},
        {"plan_name": "standard", "price": 58000},
        {"plan_name": "premium", "price": 99000}
    ]

    for data in plan_data:
        # 중복 체크 (plan_name이 unique이므로 권장)
        existing_plan = Plan.query.filter_by(plan_name=data["plan_name"]).first()

        if not existing_plan:
            new_plan = Plan(
                plan_name=data["plan_name"],
                price=data["price"]
            )
            db.session.add(new_plan)
            print(f"✅ {data['plan_name']} 요금제가 추가되었습니다.")
        else:
            print(f"⚠️ {data['plan_name']} 요금제가 이미 존재합니다.")

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"❌ 오류 발생: {e}")


# 실행
if __name__ == "__main__":
    with app.app_context():
        seed_plans()