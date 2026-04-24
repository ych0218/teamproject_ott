
from flask import Blueprint, redirect, render_template, url_for, session, flash
from ..models import Video, Plan, User, db
import random

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
    user_id = session.get('user')
    user_data = User.query.get(user_id) if user_id else None
    
    # 모든 비디오 가져오기
    all_videos = Video.query.order_by(Video.video_unique_id.desc()).all()

    # 속성 이름을 video_genres로 수정
    video_sections = [
        {
            'title': '자기전 보기좋은 드라마', 
            'list': [v for v in all_videos if v.video_genres and '드라마' in v.video_genres][17:29]
        },
        {
            'title': '지금 방영중인 예능', 
            'list': [v for v in all_videos if v.video_genres and '예능' in v.video_genres][10:24]
        },
        {
            'title': '인기 영화', 
            'list': [v for v in all_videos if v.video_genres and '영화' in v.video_genres][12:24]
        },
        {
            'title': '박진감 넘치는 액션', 
            'list': [v for v in all_videos if v.video_genres and '액션' in v.video_genres][3:15]
        }
    ]

    return render_template('main/main.html', 
                           video_sections=video_sections, 
                           video_list=all_videos, 
                           user=user_data)


@bp.route('/drama')
def drama():
    # 1. 드라마 전체 데이터
    all_dramas = Video.query.filter(Video.video_genres.like('%드라마%'))\
                            .order_by(Video.video_unique_id.desc()).all()
    
    # 2. 헤더에 쓸 ID 고정
    header_ids = [134, 135]
    
    # 3. 하단 리스트용: 헤더 ID를 제외한 나머지 드라마들만 필터링
    # v.video_unique_id가 header_ids에 포함되지 않은 것만 골라냅니다.
    filtered_dramas = [v for v in all_dramas if v.video_unique_id not in header_ids]

    # 4. TOP 10 고정 (제외된 리스트 중 상위 10개)
    top10_videos = filtered_dramas[:10]

    # 5. 하단 섹션용 (제외된 리스트 중 랜덤)
    random_drama_pool = random.sample(filtered_dramas, min(len(filtered_dramas), 36))

    return render_template('main/drama.html', 
                           video_list=all_dramas,      # 헤더용 (전체)
                           top10_list=top10_videos,    # 섹션용 (제외됨)
                           random_list=random_drama_pool)


@bp.route('/movie')
def movie():
    user_id = session.get('user')
    user_data = User.query.get(user_id) if user_id else None
    
    # 1. 영화 데이터 전체 (최신순)
    movie_data = Video.query.filter(Video.video_genres.like('%영화%'))\
                            .order_by(Video.video_unique_id.desc()).all()
    
    # 2. 헤더 전용 ID (예: 100번, 101번 영화는 배너 전용)
    header_ids = [130, 131] 
    
    # 3. 하단 섹션용 필터링 (헤더 ID 제외)
    filtered_data = [v for v in movie_data if v.video_unique_id not in header_ids]
    
    # 4. TOP 10 고정 & 하단 섹션 랜덤
    top10_videos = filtered_data[:10]
    random_movies = random.sample(filtered_data, min(len(filtered_data), 36))
    
    return render_template('main/movie.html', 
                           video_list=movie_data, 
                           top10_list=top10_videos, 
                           random_list=random_movies,
                           user=user_data)

@bp.route('/entertainment')
def entertainment():
    user_id = session.get('user')
    user_data = User.query.get(user_id) if user_id else None
    
    entertainment_data = Video.query.filter(Video.video_genres.like('%예능%'))\
                                    .order_by(Video.video_unique_id.desc()).all()
    
    # 예능 헤더 전용 ID (예: 200번, 201번)
    header_ids = [132, 133]
    
    filtered_data = [v for v in entertainment_data if v.video_unique_id not in header_ids]
    
    top10_videos = filtered_data[:10]
    random_ents = random.sample(filtered_data, min(len(filtered_data), 36))
    
    return render_template('main/entertainment.html', 
                           video_list=entertainment_data, 
                           top10_list=top10_videos, 
                           random_list=random_ents,
                           user=user_data)

@bp.route('/anime')
def anime():
    user_id = session.get('user')
    user_data = User.query.get(user_id) if user_id else None
    
    anime_data = Video.query.filter(Video.video_genres.like('%애니%'))\
                            .order_by(Video.video_unique_id.desc()).all()
    
    # 애니 헤더 전용 ID (예: 300번, 301번)
    header_ids = [87, 129]
    
    filtered_data = [v for v in anime_data if v.video_unique_id not in header_ids]
    
    top10_videos = filtered_data[:10]
    random_animes = random.sample(filtered_data, min(len(filtered_data), 36))
    
    return render_template('main/anime.html', 
                           video_list=anime_data, 
                           top10_list=top10_videos, 
                           random_list=random_animes,
                           user=user_data)


@bp.route('/support_check')
def support_check():
    # 1. 세션에 유저 정보가 있는지 확인
    if session.get('user'):
        # 2. 로그인 상태면 고객센터 페이지로 (mypage 블루프린트의 support_center 함수)
        return redirect(url_for('mypage.support_center'))
    else:
        # 3. 로그인 안 되어 있으면 로그인 페이지로 (auth 블루프린트의 login 함수)
        return redirect(url_for('auth.login'))


