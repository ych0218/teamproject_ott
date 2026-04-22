import random
from datetime import datetime, timedelta, timezone
from one import db, create_app
from one.models import Notice

app = create_app()
# 시드 데이터 생성 함수
def seed_notices():
    # 고정글 15개 + 일반글 85개 = 총 100개
    pinned_count = 15
    normal_count = 85

    # 관리자 ID (이미 DB에 존재하는 admin_unique_id 중 하나를 가정)
    admin_id = 1

    notices = []

    # 1. 고정 게시글 (is_pinned=True) 생성
    for i in range(1, pinned_count + 1):
        notice = Notice(
            admin_unique_id=admin_id,
            title=f"[필독] 중요 공지사항 제 {i}호",
            content=f"이것은 상단에 고정되는 {i}번째 중요 공지 내용입니다.",
            is_pinned=True,
            view_count=random.randint(100, 500),
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))
        )
        notices.append(notice)

    # 2. 일반 게시글 (is_pinned=False) 생성
    for i in range(1, normal_count + 1):
        notice = Notice(
            admin_unique_id=admin_id,
            title=f"일반 공지사항 안내 - {i}번",
            content=f"안녕하세요. {i}번째 일반 공지사항의 상세 내용입니다.",
            is_pinned=False,
            view_count=random.randint(0, 99),
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(31, 365))
        )
        notices.append(notice)

    # DB 반영
    db.session.add_all(notices)
    db.session.commit()
    print(f"✅ 성공: {len(notices)}개의 공지사항 데이터가 생성되었습니다.")
if __name__ == "__main__":
    with app.app_context():
        seed_notices()
# 실행 (Flask context 내부에서 호출)
# seed_notices()
