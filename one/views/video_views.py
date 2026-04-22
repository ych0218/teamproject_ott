from flask import Blueprint, render_template
from ..models import Video

bp = Blueprint('video', __name__, url_prefix='/video')


# 목록 페이지
@bp.route('/list')
def list():
    video_list = Video.query.order_by(Video.video_unique_id.desc()).all()
    return render_template('main/main.html', video_list=video_list)


# 상세(재생) 페이지
@bp.route('/detail/<int:video_id>')
def detail(video_id):
    video = Video.query.get_or_404(video_id)
    return render_template('sub/sub.html', video=video)