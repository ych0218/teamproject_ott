import random
from datetime import datetime, timedelta, timezone

from werkzeug.security import generate_password_hash

from one import db, create_app
from one.models import Admin

app = create_app()


def seed_admin():
    with app.app_context():
        # 1. 이미 관리자가 있는지 확인 (중복 생성 방지)
        existing_admin = Admin.query.filter_by(admin_id='admin').first()

        if not existing_admin:
            print("관리자 계정 생성을 시작합니다...")

            # 2. 새 관리자 객체 생성
            new_admin = Admin(
                admin_id='admin@gmail.com',  # 로그인 아이디
                admin_password=generate_password_hash('admin1234'),  # 암호화된 비밀번호
                admin_name='최고관리자',
                admin_role='superadmin'
            )

            # 3. DB 저장
            db.session.add(new_admin)
            db.session.commit()

            print("✅ 관리자 계정이 성공적으로 생성되었습니다!")
            print("아이디: admin / 비밀번호: admin1234")
        else:
            print("ℹ️ 이미 'admin' 아이디가 존재합니다. 생성을 건너뜁니다.")


if __name__ == "__main__":
    seed_admin()