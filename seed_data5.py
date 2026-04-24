from datetime import datetime, timedelta, timezone
import random

from one import create_app, db
from one.models import Review  # 실제 모델 파일명으로 수정

app = create_app()
def seed_sorting_test_reviews():
    # 테스트 설정
    target_video_id = 1
    user_ids = range(2, 10)  # 2부터 9까지

    # 순차적으로 시간이 흐르는 것처럼 만들기 위해 base_time 설정
    base_time = datetime.now(timezone.utc) - timedelta(hours=10)

    test_reviews = []

    # 리뷰 문구 리스트
    comments = [
        "이거 진짜 재밌나요?",
        "생각보다 별로인 듯..",
        "인생 작입니다 꼭 보세요!",
        "배우들 연기가 장난 아니네요.",
        "음악이 너무 좋아요.",
        "주말에 정주행 완료했습니다.",
        "친구한테 추천받아서 왔어요.",
        "정렬 테스트용 마지막 댓글입니다 (유저 2번)"
    ]

    for i, user_id in enumerate(user_ids):
        # 유저 2번의 댓글을 가장 '최신'으로 만들기 위해 시간을 조절합니다.
        # i가 커질수록 더 나중에 쓴 글이 됩니다.
        review_time = base_time + timedelta(minutes=i * 10)

        new_review = Review(
            user_unique_id=user_id,
            video_unique_id=target_video_id,
            comment=comments[i % len(comments)],
            rating=random.randint(3, 5),
            is_spoiler=False,
            create_at=review_time,
            update_at=review_time
        )
        test_reviews.append(new_review)

    try:
        db.session.add_all(test_reviews)
        db.session.commit()
        print(f"✅ 비디오 {target_video_id}번에 대한 8개의 테스트 리뷰가 생성되었습니다.")
    except Exception as e:
        db.session.rollback()
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    # app 객체를 불러옵니다 (본인의 app 생성 함수나 변수명에 맞게 수정)

    with app.app_context():
        seed_sorting_test_reviews()