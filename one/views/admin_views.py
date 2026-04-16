from flask import Blueprint, render_template, redirect, url_for, request
from sqlalchemy import or_
from one import db
from one.models import User, Video, Support, Review
from datetime import datetime

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
def admin_main():
    return render_template('admin/admin_main.html')


# ================= 회원 관리 =================
@bp.route('/members')
def member_list():
    keyword = request.args.get('keyword', '').strip()

    query = User.query

    if keyword:
        query = query.filter(
            or_(
                User.user_name.contains(keyword),
                User.user_email.contains(keyword),
                User.user_phone.contains(keyword)
            )
        )

    member_list = query.order_by(User.user_unique_id.desc()).all()
    return render_template(
        'admin/member_list.html',
        member_list=member_list,
        keyword=keyword
    )


# ================= 활성 / 비활성 토글 =================
@bp.route('/members/toggle/<int:user_id>', methods=['POST'])
def member_toggle(user_id):
    member = User.query.get_or_404(user_id)
    member.user_active = not member.user_active
    db.session.commit()
    return redirect(url_for('admin.member_list', changed=1))


# ================= 콘텐츠 관리 =================
@bp.route('/contents')
def content_list():
    keyword = request.args.get('keyword', '').strip()

    query = Video.query

    if keyword:
        query = query.filter(
            or_(
                Video.video_title.contains(keyword),
                Video.video_director.contains(keyword),
                Video.video_actor.contains(keyword)
            )
        )

    content_list = query.order_by(Video.video_unique_id.desc()).all()

    return render_template(
        'admin/content_list.html',
        content_list=content_list,
        keyword=keyword
    )


# ================= 콘텐츠 등록 =================
@bp.route('/contents/create', methods=['GET', 'POST'])
def content_create():
    if request.method == 'POST':
        video_title = request.form.get('video_title', '').strip()
        video_director = request.form.get('video_director', '').strip()
        video_actor = request.form.get('video_actor', '').strip()
        video_age_limit = request.form.get('video_age_limit', '').strip()
        video_date_str = request.form.get('video_date', '').strip()
        video_url = request.form.get('video_url', '').strip()
        video_thumbnail = request.form.get('video_thumbnail', '').strip()
        video_synopsis = request.form.get('video_synopsis', '').strip()
        video_genres = request.form.get('video_genres', '').strip()
        video_is_movie = request.form.get('video_is_movie') == 'True'

        video_date = None
        if video_date_str:
            video_date = datetime.strptime(video_date_str, '%Y-%m-%d').date()

        new_video = Video(
            video_title=video_title,
            video_director=video_director,
            video_actor=video_actor,
            video_age_limit=video_age_limit,
            video_date=video_date,
            video_url=video_url,
            video_thumbnail=video_thumbnail,
            video_synopsis=video_synopsis,
            video_genres=video_genres,
            video_is_movie=video_is_movie,
            admin_unique_id=1
        )

        db.session.add(new_video)
        db.session.commit()
        return redirect(url_for('admin.content_list'))

    return render_template(
        'admin/content_form.html',
        mode='create',
        content=None
    )


# ================= 콘텐츠 수정 =================
@bp.route('/contents/edit/<int:video_id>', methods=['GET', 'POST'])
def content_edit(video_id):
    content = Video.query.get_or_404(video_id)

    if request.method == 'POST':
        content.video_title = request.form.get('video_title', '').strip()
        content.video_director = request.form.get('video_director', '').strip()
        content.video_actor = request.form.get('video_actor', '').strip()
        content.video_age_limit = request.form.get('video_age_limit', '').strip()

        video_date_str = request.form.get('video_date', '').strip()
        content.video_date = datetime.strptime(video_date_str, '%Y-%m-%d').date() if video_date_str else None

        content.video_url = request.form.get('video_url', '').strip()
        content.video_thumbnail = request.form.get('video_thumbnail', '').strip()
        content.video_synopsis = request.form.get('video_synopsis', '').strip()
        content.video_genres = request.form.get('video_genres', '').strip()
        content.video_is_movie = request.form.get('video_is_movie') == 'True'

        db.session.commit()
        return redirect(url_for('admin.content_list'))

    return render_template(
        'admin/content_form.html',
        mode='edit',
        content=content
    )


# ================= 콘텐츠 삭제 =================
@bp.route('/contents/delete/<int:video_id>', methods=['POST'])
def content_delete(video_id):
    content = Video.query.get_or_404(video_id)
    db.session.delete(content)
    db.session.commit()
    return redirect(url_for('admin.content_list'))


# ================= 문의 관리 =================
@bp.route('/inquiries')
def inquiry_list():
    inquiry_list = Support.query.order_by(Support.support_id.desc()).all()
    return render_template(
        'admin/inquiry_list.html',
        inquiry_list=inquiry_list
    )


# ================= 리뷰 관리 =================
@bp.route('/reviews')
def review_list():
    review_list = Review.query.order_by(Review.review_id.desc()).all()
    return render_template(
        'admin/review_list.html',
        review_list=review_list
    )