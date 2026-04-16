from one import db
from datetime import datetime, timezone


# https://blog.naver.com/red0808/223888577210
class User (db.Model):
    __tablename__ = 'user'
    # 프라이머리 키
    user_unique_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 사용자 기본 정보
    # user_id = db.Column(db.String(50), unique=True)  # 로그인 아이디
    user_password = db.Column(db.String(200), nullable=True)  # 암호화된 비번
    user_email = db.Column(db.String(100), unique=True, nullable=False)  # 이메일

    user_name = db.Column(db.String(50))  # 이름
    user_birth = db.Column(db.DateTime, nullable=True)  # 생년월일
    user_phone = db.Column(db.String(20), nullable=True)  # 고유값, 필수값 설정 핸드폰 번호
    user_gender = db.Column(db.String(10), nullable=True)  # 성별 (M/F 등)

    # [추가] 1. 어떤 방식으로 처음 가입했는지 (통계 및 본인인증용)
    signup_method = db.Column(db.String(20), default='email')  # 'email' 또는 'kakao'

    # [추가] 2. 카카오 연동 여부를 확인하는 고유 식별자
    # 이 값이 NULL이면 연동 안됨, 값이 있으면 연동됨!
    kakao_id = db.Column(db.String(100), unique=True, nullable=True)
    # [추가] 3. 네이버 연동
    naver_id = db.Column(db.String(100), unique=True, nullable=True)
    user_active = db.Column(db.Boolean, nullable=False,default=True)  # 활성화된 유저인지, 차단(블락된)유저인지 True는 로그인가능 False는 로그인 불가능

    # --- 관계 설정 (Relationship) ---
    # 다른 테이블에서 이 사용자를 참조할 때 편리하게 가져오기 위함입니다.

    # 1:N 관계 (구독, 시청기록, 리뷰, 문의 등)
    subscriptions = db.relationship('Subscription', backref='user', lazy=True)
    watch_histories = db.relationship('WatchHistory', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    supports = db.relationship('Support', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)
    # backref -> 역참조 : 리뷰 입장에서 작성자를 바로 알고 싶거나 할때 사용
    # lazy : 성능을 위한 설정. 예를들어 유저 정보를 불러올 때 오든 리뷰, 시청기록 등을 다 가져오지 말고
    # 필요할때, 호출을 직접 할때만 DB에서 가져오라는 뜻

    # 찜하기 & 좋아요 (M:N 성격의 1:N)
    likes = db.relationship('VideoLike', backref='user', lazy=True)
    wishlist = db.relationship('VideoWish', backref='user', lazy=True)

    # __repr__ 매직메서드중 하나 : 객체를 출력했을 때 어떻게 보여줄 것인지.
    # 예를들어 print(user)를 할 경우 메모리 주소값이 나오게 되는데 이 함수가 있으면 f-string를 통해 user아이디를 보여준다.
    # 관례적으로 개발자가 코드를 짜고 디버깅할 때 편하기 위해 꼭 넣는 코드라 해서 넣어봄
    def __repr__(self):
        return f'<User {self.email}>'


class Video(db.Model):
    __tablename__ = 'video'
    # 프라이머리 키
    video_unique_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 영상 상세 정보
    video_title = db.Column(db.String(200), nullable=False)  # 제목
    video_director = db.Column(db.String(100))  # 감독
    video_actor = db.Column(db.String(255))  # 출연진
    video_url = db.Column(db.String(500), nullable=False)  # 실제 영상 주소
    video_thumbnail = db.Column(db.String(500), nullable=False)  # 썸네일 이미지 주소
    video_date = db.Column(db.Date)  # 개봉/등록 날짜
    video_age_limit = db.Column(db.String(20))  # 시청 등급 (예: 15세, All)
    video_synopsis = db.Column(db.Text)  # 줄거리요약
    video_is_movie = db.Column(db.Boolean, default=True)
    video_genres = db.Column(db.String(100))
    # --- 관계 설정 (Relationship) ---

    # --- 외래 키 (Foreign Key) ---
    # 이 비디오를 등록한 관리자 ID
    admin_unique_id = db.Column(db.Integer, db.ForeignKey('admin.admin_unique_id'), nullable=False)

    # 2. 1:N 관계 (시청 기록, 리뷰, 좋아요, 찜하기 등)
    # cascade 설정 추가 (부모 삭제 시 자식 자동 삭제)
    watch_histories = db.relationship('WatchHistory', backref='video', lazy=True, cascade="all, delete-orphan")
    reviews = db.relationship('Review', backref='video', lazy=True, cascade="all, delete-orphan")
    likes = db.relationship('VideoLike', backref='video', lazy=True, cascade="all, delete-orphan")
    wishes = db.relationship('VideoWish', backref='video', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Video {self.video_title}>'

class VideoLike(db.Model):
    __tablename__ = 'videos_like' # ERD에 표기된 이름으로 맞춤

    # 프라이머리 키
    like_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 외래키 연결 (타입 일관성을 위해 Integer 권장)
    user_unique_id = db.Column(db.Integer, db.ForeignKey('user.user_unique_id'), nullable=False)
    video_unique_id = db.Column(db.Integer, db.ForeignKey('video.video_unique_id'), nullable=False)

    # 생성일 (타임존을 포함한 현재 시간 설정)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # 중복 좋아요 방지 제약조건
    __table_args__ = (
        db.UniqueConstraint('user_unique_id', 'video_unique_id', name='_user_video_like_uc'),
    )

    def __repr__(self):
        return f'<Like User:{self.user_unique_id} Video:{self.video_unique_id}>'


# 2. 찜하기 테이블 (VideoWish)
class VideoWish(db.Model):
    __tablename__ = 'videos_wish'  # ERD 표기명과 일치

    # 프라이머리 키
    wish_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 외래키 연결 (누가, 어떤 영상에)
    # 외래키 연결 (User/Video의 타입과 맞춰 Integer 권장)
    user_unique_id = db.Column(db.Integer, db.ForeignKey('user.user_unique_id'), nullable=False)
    video_unique_id = db.Column(db.Integer, db.ForeignKey('video.video_unique_id'), nullable=False)

    # 생성일 (언제 찜했는지 - 마이페이지 정렬용)
    # 생성일 (nullable=False이므로 기본값을 넣어주는 것이 편리합니다)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # 중복 찜하기 방지
    __table_args__ = (
        db.UniqueConstraint('user_unique_id', 'video_unique_id', name='_user_video_wish_uc'),
    )

    def __repr__(self):
        return f'<Wish User:{self.user_unique_id} Video:{self.video_unique_id}>'


class Review(db.Model):
    __tablename__ = 'reviews'  # ERD 표기명과 일치
    # 프라이머리 키
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 외래키 연결 (누가, 어떤 영상에)
    user_unique_id = db.Column(db.Integer, db.ForeignKey('user.user_unique_id'), nullable=False)
    video_unique_id = db.Column(db.Integer, db.ForeignKey('video.video_unique_id'), nullable=False)

    # 리뷰 내용 및 별점
    comment = db.Column(db.Text, nullable=False)  # 후기 내용
    rating = db.Column(db.Integer, nullable=False)  # 별점 (예: 1~5)

    # 부가 기능
    is_spoiler = db.Column(db.Boolean, default=False)  # 스포일러 여부

    # 날짜 관리 (timezone.utc 권장)
    create_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 작성일
    update_at = db.Column(db.DateTime,
                          default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))  # 수정일

    def __repr__(self):
        return f'<Review Video:{self.video_unique_id} Rating:{self.rating}>'


# 1. 요금제 테이블 (plan 테이블)
class Plan(db.Model):
    __tablename__ = 'plan'

    plan_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # 금액
    plan_name = db.Column(db.String(50), nullable=False, unique=True)  # 요금제 이름, 중복x

    # 역참조 설정
    # Subscription 모델에서 plan.plan_name 등으로 접근 가능하게 해줍니다.
    subscriptions = db.relationship('Subscription', backref='plan', lazy=True)

    def __repr__(self):
        return f'<Plan {self.plan_name}>'


# 2. 구독 테이블 (subscription 테이블)
class Subscription(db.Model):
    __tablename__ = 'subscription'

    # 프라이머리 키
    subscription_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 외래키 연결
    user_unique_id = db.Column(db.Integer, db.ForeignKey('user.user_unique_id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.plan_id'), nullable=False)

    start_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 시작일
    end_date = db.Column(db.DateTime, nullable=False)  # 종료일 (이미지 중복분 통합)

    # 상태 관리 (예: active, expired, canceled, pending) 결제하면 바로 active가 되기에 default값 부여
    status = db.Column(db.String(20), default='active')

    # 관계 설정: 결제 내역 (1:N)
    # 한 번의 구독(연장 포함)에 여러 결제 시도가 있을 수 있으므로 1:N으로 설정하는 경우가 많습니다.
    payments = db.relationship('Payment', backref='subscription', lazy=True)

# 배치 작업: 나중에 end_date가 현재 시간보다 과거인 데이터를 찾아 status를 'expired'로 바꾸는 간단한 스케줄러(예: Celery, Flask-APScheduler)를 연동하면 관리가 편해집니다.
    def __repr__(self):
        return f'<Subscription User:{self.user_unique_id} Plan:{self.plan_id}>'


# 질문 테이블
class Support(db.Model):
    __tablename__ = 'support'

    # 프라이머리 키
    support_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 외래키 연결
    user_unique_id = db.Column(db.Integer, db.ForeignKey('user.user_unique_id'), nullable=False)

    # 문의 내용
    category = db.Column(db.String(50))  # 문의 유형 (결제문의, 영상오류 등)
    title = db.Column(db.String(255), nullable=False)  # 제목
    content = db.Column(db.Text, nullable=False)  # 내용

    # 상태 관리 (접수, 처리중, 완료 등 / 영문 권장: pending, processing, completed)
    status = db.Column(db.String(20), nullable=False, default='pending')

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    image_url = db.Column(db.String(500))  # 이미지 첨부 경로

    # 답변과의 관계 (1:N)
    answers = db.relationship('SupportAnswer', backref='support', lazy=True, cascade="all, delete-orphan")


# 답변 테이블
class SupportAnswer(db.Model):
    __tablename__ = 'support_answer'

    # 프라이머리 키
    answer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 외래키: 어떤 문의글에 대한 답변인가
    support_id = db.Column(db.Integer, db.ForeignKey('support.support_id'), nullable=False)

    # 외래키: 어떤 관리자가 답변을 작성했는가
    admin_unique_id = db.Column(db.Integer, db.ForeignKey('admin.admin_unique_id'), nullable=False)


    content = db.Column(db.Text)  # 답변 내용
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# 시청 기록 테이블 (이어보기용)
class WatchHistory(db.Model):
    __tablename__ = 'watch_history'

    # 프라이머리 키
    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 외래키 연결
    user_unique_id = db.Column(db.Integer, db.ForeignKey('user.user_unique_id'), nullable=False)
    video_unique_id = db.Column(db.Integer, db.ForeignKey('video.video_unique_id'), nullable=False)

    # 시청 정보
    last_played_time = db.Column(db.Integer, default=0)  # 초 단위 지점 (예: 120초 지점까지 봄)
    is_finished = db.Column(db.Boolean, default=False)  # 다 봤는지 여부 (엔딩 크레딧 기준 등)

    # [추가] 마지막 시청 시간 (최근 본 영상 목록 정렬용)
    updated_at = db.Column(db.DateTime,
                          default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))

# 결제 테이블
class Payment(db.Model):

    __tablename__ = 'payments'  # ERD 상의 이름과 일치

    # 프라이머리 키
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 외래키 연결
    user_unique_id = db.Column(db.Integer, db.ForeignKey('user.user_unique_id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.subscription_id'), nullable=False)


    # 결제 정보
    price = db.Column(db.Numeric(10, 2))  # 결제 금액
    status = db.Column(db.String(20))  # 결제 상태 (성공, 환불 등)
    paid_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Notice(db.Model):
    __tablename__ = 'notice'

    # 프라이머리 키
    notice_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # [ERD 반영] 작성자 외래키: 어떤 관리자가 작성했는가
    admin_unique_id = db.Column(db.Integer, db.ForeignKey('admin.admin_unique_id'), nullable=False)
    # 작성한 관리자의 ID를 참조합니다.
    # 공지사항 내용
    title = db.Column(db.String(255), nullable=False)  # 제목
    content = db.Column(db.Text, nullable=False)  # 내용

    # 부가 기능
    is_pinned = db.Column(db.Boolean, default=False)  # 상단 고정 여부 (True: 고정)
    view_count = db.Column(db.Integer, default=0)  # 조회수

    # 작성일
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    # --- 외래 키 (Foreign Key) ---


    def __repr__(self):
        return f'<Notice {self.title}>'

class Admin(db.Model):
    __tablename__ = 'admin'

    # 프라이머리 키
    admin_unique_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 관리자 로그인 정보
    admin_id = db.Column(db.String(50), unique=True, nullable=False)  # 로그인 아이디
    admin_password = db.Column(db.String(255), nullable=False)  # 암호화된 비밀번호
    admin_name = db.Column(db.String(50), nullable=False)  # 관리자 이름

    # 관리자 권한 (예: superadmin, editor, cs)
    # 권한에 따라 메뉴 접근 제한을 두기 위해 추가하는 것이 좋습니다.
    admin_role = db.Column(db.String(20), default='staff')

    # --- 관계 설정 (Relationship) ---
    # 관리자가 수행한 활동들을 추적하기 위한 역참조들입니다.

    # 1. 관리자가 등록한 영상들
    videos = db.relationship('Video', backref='admin', lazy=True)

    # 2. 관리자가 작성한 공지사항들
    notices = db.relationship('Notice', backref='admin', lazy=True)

    # 3. 관리자가 작성한 고객지원 답변들
    answers = db.relationship('SupportAnswer', backref='admin', lazy=True)

    def __repr__(self):
        return f'<Admin {self.admin_id} ({self.admin_name})>'
