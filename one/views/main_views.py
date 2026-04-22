from flask import Blueprint, redirect, render_template, url_for, session
from ..models import Video, Plan

bp=Blueprint('home',__name__,url_prefix='/')

@bp.route('/')
def index():
    if session.get('user'):
        return redirect(url_for('home.main'))

    video_list = Video.query.order_by(Video.video_unique_id.desc()).all()
    plan_list = Plan.query.order_by(Plan.price.asc()).all()

    return render_template(
        'main/home.html',
        video_list=video_list,
        plans=plan_list
    )

@bp.route('/home')
def home():
    video_list = Video.query.order_by(Video.video_unique_id.desc()).all()
    plan_list = Plan.query.order_by(Plan.price.asc()).all()
    return render_template('main/home.html', video_list=video_list,
                           plans=plan_list)


@bp.route('/main')
def main():
    video_list = Video.query.order_by(Video.video_unique_id.desc()).all()

    # 2. 템플릿에 video_list 데이터를 전달합니다.
    # 기존에 'main.html'을 사용 중이라면 아래와 같이 작성합니다.
    return render_template('main/main.html', video_list=video_list)

@bp.route('/movie')
def movie():
    return render_template('main/movie.html')

@bp.route('/drama')
def drama():
    # DB에서 드라마 데이터만 가져오기 (예시)
    return render_template('main/drama.html')

@bp.route('/entertainment')
def entertainment():
    return render_template('main/entertainment.html')

@bp.route('/anime')
def anime():
    return render_template('main/anime.html')


