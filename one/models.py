from one import db
from datetime import datetime, timezone


# https://blog.naver.com/red0808/223888577210
class users(db.Model):
    __tablename__ = 'user'
    # 프라이머리 키
    user_unique_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # 사용자 기본 정보
    user_id = db.Column(db.String(50), unique=True, nullable=False)  # 로그인 아이디
    user_password = db.Column(db.String(255), nullable=False)  # 암호화된 비번
    user_email = db.Column(db.String(100), unique=True, nullable=False)  # 이메일
    user_name = db.Column(db.String(50), nullable=False)  # 이름
    user_birth = db.Column(db.Date)  # 생년월일
    user_phone = db.Column(db.String(20), unique=True, nullable=False)  # 고유값, 필수값 설정 핸드폰 번호
    user_gender = db.Column(db.String(10))  # 성별 (M/F 등)

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
        return f'<User {self.user_id}>'

    # 1. 연결 테이블 (M:N 관계의 징검다리)
    # 실제 클래스로 만들지 않고 db.Table을 사용하는 것이 조인(Join) 시 성능과 관리에 유리.


video_genres = db.Table('video_genres',
                        db.Column('video_unique_id', db.BigInteger, db.ForeignKey('video.video_unique_id'),
                                  primary_key=True),
                        db.Column('genre_id', db.Integer, db.ForeignKey('genre.genre_id'), primary_key=True)
                        )


class Video(db.Model):
    # 프라이머리 키
    video_unique_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # 영상 상세 정보 (이미지의 컬럼 반영)
    video_title = db.Column(db.String(200), nullable=False)  # 제목
    video_director = db.Column(db.String(100))  # 감독
    video_actor = db.Column(db.String(255))  # 출연진
    video_url = db.Column(db.String(500), nullable=False)  # 실제 영상 주소
    video_thumbnail = db.Column(db.String(500), nullable=False)  # 썸네일 이미지 주소
    video_date = db.Column(db.Date)  # 개봉/등록 날짜
    video_age_limit = db.Column(db.String(20))  # 시청 등급 (예: 15세, All)
    video_synopsis = db.Column(db.Text)  # 줄거리요약

    # --- 관계 설정 (Relationship) ---

    # 1. 장르와 다대다(M:N) 연결
    # secondary 설정을 통해 미리 만들어둔 video_genres 테이블을 거쳐 Genre 테이블과 연결됩니다.
    # lazy='dynamic' 데이터를 가져오기전 추가 조건을 걸 수 있는 쿼리형태로 넘어옴.(데이터가 많을 경우 최적화를 위해 사용)
    # True같은 경우 파이썬 리스트로 넘어옴.
    genres = db.relationship('Genre', secondary=video_genres, backref=db.backref('videos', lazy='dynamic'))

    # --- 외래 키 (Foreign Key) ---
    # 이 비디오를 등록한 관리자 ID
    admin_unique_id = db.Column(db.BigInteger, db.ForeignKey('admin.admin_unique_id'), nullable=False)

    # 2. 1:N 관계 (시청 기록, 리뷰, 좋아요, 찜하기 등)
    watch_histories = db.relationship('WatchHistory', backref='video', lazy=True)
    reviews = db.relationship('Review', backref='video', lazy=True)
    likes = db.relationship('VideoLike', backref='video', lazy=True)
    wishlist = db.relationship('VideoWish', backref='video', lazy=True)

    def __repr__(self):
        return f'<Video {self.video_title}>'


# 2. 장르 테이블
class Genre(db.Model):
    genre_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    genre_name = db.Column(db.String(50), unique=True, nullable=False)  # 액션, 로맨스, SF 등

    def __repr__(self):
        return f'<Genre {self.genre_name}>'


class VideoLike(db.Model):

    # 프라이머리 키
    like_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # 외래키 연결 (누가, 어떤 영상에)
    user_unique_id = db.Column(db.BigInteger, db.ForeignKey('user.user_unique_id'), nullable=False)
    video_unique_id = db.Column(db.BigInteger, db.ForeignKey('video.video_unique_id'), nullable=False)

    # 생성일 (언제 눌렀는지)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 한 유저가 같은 영상에 좋아요를 중복으로 누르지 못하게 제약조건 추가
    __table_args__ = (
        db.UniqueConstraint('user_unique_id', 'video_unique_id', name='_user_video_like_uc'),
    )

    def __repr__(self):
        return f'<Like User:{self.user_unique_id} Video:{self.video_unique_id}>'


# 2. 찜하기 테이블 (VideoWish)
class VideoWish(db.Model):

    # 프라이머리 키
    wish_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # 외래키 연결 (누가, 어떤 영상에)
    user_unique_id = db.Column(db.BigInteger, db.ForeignKey('user.user_unique_id'), nullable=False)
    video_unique_id = db.Column(db.BigInteger, db.ForeignKey('video.video_unique_id'), nullable=False)

    # 생성일 (언제 찜했는지 - 마이페이지 정렬용)
    created_at = db.Column(db.DateTime, nullable=False)

    # 중복 찜하기 방지
    __table_args__ = (
        db.UniqueConstraint('user_unique_id', 'video_unique_id', name='_user_video_wish_uc'),
    )

    def __repr__(self):
        return f'<Wish User:{self.user_unique_id} Video:{self.video_unique_id}>'


class Review(db.Model):

    # 프라이머리 키
    review_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # 외래키 연결 (누가, 어떤 영상에)
    user_unique_id = db.Column(db.BigInteger, db.ForeignKey('user.user_unique_id'), nullable=False)
    video_unique_id = db.Column(db.BigInteger, db.ForeignKey('video.video_unique_id'), nullable=False)

    # 리뷰 내용 및 별점
    comment = db.Column(db.Text, nullable=False)  # 후기 내용
    rating = db.Column(db.Integer, nullable=False)  # 별점 (예: 1~5)

    # 부가 기능
    is_spoiler = db.Column(db.Boolean, default=False)  # 스포일러 여부

    # 날짜 관리
    create_at = db.Column(db.DateTime, default=datetime.utcnow)  # 작성일
    update_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 수정일

    def __repr__(self):
        return f'<Review Video:{self.video_unique_id} Rating:{self.rating}>'


# 1. 요금제 테이블 (plan 테이블)
class Plan(db.Model):

    plan_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # 금액
    plan_name = db.Column(db.String(50), nullable=False)  # 요금제 이름

    # 역참조 설정
    subscriptions = db.relationship('Subscription', backref='plan', lazy=True)

    def __repr__(self):
        return f'<Plan {self.plan_name}>'


# 2. 구독 테이블 (subscription 테이블)
class Subscription(db.Model):

    subscription_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_unique_id = db.Column(db.BigInteger, db.ForeignKey('user.user_unique_id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.plan_id'), nullable=False)

    start_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 시작일
    end_date = db.Column(db.DateTime, nullable=False)  # 종료일 (이미지 중복분 통합)
    status = db.Column(db.String(20))  # 상태 (active 등)

    def __repr__(self):
        return f'<Subscription User:{self.user_unique_id} Plan:{self.plan_id}>'


# 질문 테이블
class Support(db.Model):

    support_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_unique_id = db.Column(db.BigInteger, db.ForeignKey('user.user_unique_id'), nullable=False)

    category = db.Column(db.String(50))  # 문의 유형
    title = db.Column(db.String(255))  # 제목
    content = db.Column(db.Text)  # 내용
    status = db.Column(db.String(20))  # 상태 (접수, 완료 등)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    image_url = db.Column(db.String(500))  # 이미지 첨부 경로

    # 답변과의 관계 (1:N)
    answers = db.relationship('SupportAnswer', backref='support', lazy=True)


# 답변 테이블
class SupportAnswer(db.Model):

    answer_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    support_id = db.Column(db.BigInteger, db.ForeignKey('support.support_id'), nullable=False)

    admin_id = db.Column(db.BigInteger)  # 관리자 식별 ID
    content = db.Column(db.Text)  # 답변 내용
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# 시청 기록 테이블 (이어보기용)
class WatchHistory(db.Model):

    history_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_unique_id = db.Column(db.BigInteger, db.ForeignKey('user.user_unique_id'), nullable=False)
    video_unique_id = db.Column(db.BigInteger, db.ForeignKey('video.video_unique_id'), nullable=False)

    last_played_time = db.Column(db.Integer, default=0)  # 초 단위 지점
    is_finished = db.Column(db.Boolean, default=False)  # 다 봤는지 여부


# 결제 테이블
class Payment(db.Model):

    payment_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_unique_id = db.Column(db.BigInteger, db.ForeignKey('user.user_unique_id'), nullable=False)
    subscription_id = db.Column(db.BigInteger, db.ForeignKey('subscription.subscription_id'), nullable=False)

    price = db.Column(db.Numeric(10, 2))  # 결제 금액
    status = db.Column(db.String(20))  # 결제 상태 (성공, 환불 등)
    paid_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Notice(db.Model):

    # 프라이머리 키
    notice_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # 공지사항 내용
    title = db.Column(db.String(255), nullable=False)  # 제목
    content = db.Column(db.Text, nullable=False)  # 내용

    # 부가 기능
    is_pinned = db.Column(db.Boolean, default=False)  # 상단 고정 여부 (True: 고정)
    view_count = db.Column(db.Integer, default=0)  # 조회수

    # 작성일
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    # --- 외래 키 (Foreign Key) ---
    # 작성한 관리자의 ID를 참조합니다.
    admin_unique_id = db.Column(db.BigInteger, db.ForeignKey('admin.admin_unique_id'), nullable=False)

    def __repr__(self):
        return f'<Notice {self.title}>'


class Admin(db.Model):

    # 프라이머리 키
    admin_unique_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # 관리자 기본 정보
    admin_id = db.Column(db.String(50), unique=True, nullable=False)  # 관리자 로그인 아이디
    admin_password = db.Column(db.String(255), nullable=False)  # 암호화된 비밀번호
    admin_name = db.Column(db.String(50), nullable=False)  # 관리자 이름
    admin_role = db.Column(db.String(20), default='staff')  # 권한 레벨 (예: super, staff 등)

    # --- 관계 설정 (Relationship) ---

    # 관리자가 등록한 비디오들
    videos = db.relationship('Video', backref='admin', lazy=True)

    # 관리자가 작성한 공지사항
    notices = db.relationship('Notice', backref='admin', lazy=True)

    # 관리자가 작성한 1:1 문의 답변
    support_answers = db.relationship('SupportAnswer', backref='admin', lazy=True)

    def __repr__(self):
        return f'<Admin {self.admin_id}>'