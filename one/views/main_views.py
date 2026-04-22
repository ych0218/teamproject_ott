
from flask import Blueprint, redirect, render_template, url_for, session, flash
from ..models import Video, Plan, User, db

bp=Blueprint('home',__name__,url_prefix='/')

@bp.route('/')
def index():
    if session.get('user'):
        return redirect(url_for('home.main'))
    video_list = Video.query.order_by(Video.video_unique_id.desc()).all()
    plan_list = Plan.query.order_by(Plan.price.asc()).all()
    return render_template('main/home.html', video_list=video_list,
                           plans=plan_list)

@bp.route('/home')
def home():
    video_list = Video.query.order_by(Video.video_unique_id.desc()).all()
    plan_list = Plan.query.order_by(Plan.price.asc()).all()
    return render_template('main/home.html', video_list=video_list,
                           plans=plan_list)


@bp.route('/main')
def main():
    # 1. 세션에서 유저 ID 가져오기
    user_id = session.get('user')

    # 2. 유저 정보 조회 (로그인 안되어있으면 None)
    user_data = User.query.get(user_id) if user_id else None
    video_list = Video.query.order_by(Video.video_unique_id.desc()).all()

    # 2. 템플릿에 video_list 데이터를 전달합니다.
    # 기존에 'main.html'을 사용 중이라면 아래와 같이 작성합니다.
    return render_template('main/main.html', video_list=video_list, user=user_data)

@bp.route('/movie')
def movie():
    user_id = session.get('user')
    user_data = User.query.get(user_id) if user_id else None
    movie_data = Video.query.filter(Video.video_genres.like('%영화%')).all()
    return render_template('main/movie.html', video_list=movie_data, user=user_data)

@bp.route('/drama')
def drama():
    user_id = session.get('user')
    user_data = User.query.get(user_id) if user_id else None
    drama_data = Video.query.filter(Video.video_genres.like('%드라마%')).all()
    return render_template('main/drama.html', video_list=drama_data, user=user_data)

@bp.route('/entertainment')
def entertainment():
    user_id = session.get('user')
    user_data = User.query.get(user_id) if user_id else None
    entertainment_data = Video.query.filter(Video.video_genres.like('%예능%')).all()
    return render_template('main/entertainment.html', video_list=entertainment_data, user=user_data)

@bp.route('/anime')
def anime():
    user_id = session.get('user')
    user_data = User.query.get(user_id) if user_id else None
    # 1. DB에서 애니메이션 장르만 가져오거나 전체를 가져옵니다.
    # 만약 모델에 video_genres 필드가 있다면 아래처럼 필터링 가능합니다.
    anime_data = Video.query.filter(Video.video_genres.like('%애니%')).all()
    # 전달할 때 이름을 anime_videos로 지정!
    return render_template('main/anime.html', video_list=anime_data, user=user_data)


@bp.route('/support_check')
def support_check():
    # 1. 세션에 유저 정보가 있는지 확인
    if session.get('user'):
        # 2. 로그인 상태면 고객센터 페이지로 (mypage 블루프린트의 support_center 함수)
        return redirect(url_for('mypage.support_center'))
    else:
        # 3. 로그인 안 되어 있으면 로그인 페이지로 (auth 블루프린트의 login 함수)
        return redirect(url_for('auth.login'))


