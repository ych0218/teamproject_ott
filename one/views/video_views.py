from flask import Blueprint, render_template, session, jsonify, request
from ..models import Video, User, WatchHistory, VideoLike, VideoWish, db, Review
from datetime import datetime, timezone
bp = Blueprint('video', __name__, url_prefix='/video')


# 목록 페이지
@bp.route('/list')
def list():
    # 1. 세션에서 유저 ID 가져오기
    user_id = session.get('user')

    # 2. 유저 정보 조회 (로그인 상태면 유저 객체, 아니면 None)
    user_data = User.query.get(user_id) if user_id else None

    # 3. 비디오 목록 가져오기
    video_list = Video.query.order_by(Video.video_unique_id.desc()).all()

    # 4. user 정보를 포함하여 렌더링
    return render_template('main/main.html', video_list=video_list, user=user_data)


@bp.route('/detail/<int:video_id>')
def detail(video_id):
    user_id = session.get('user')
    video = Video.query.get_or_404(video_id)

    # [1] 유저 데이터 및 리뷰 로직 (기존 동일)
    user_data = User.query.get(user_id) if user_id else None
    all_reviews = Review.query.filter_by(video_unique_id=video_id).order_by(Review.create_at.desc()).all()
    my_reviews = [r for r in all_reviews if r.user_unique_id == user_id]
    other_reviews = [r for r in all_reviews if r.user_unique_id != user_id]
    sorted_reviews = my_reviews + other_reviews

    history = None
    is_liked = False
    is_wished = False
    if user_id:
        history = WatchHistory.query.filter_by(user_unique_id=user_id, video_unique_id=video_id).first()
        is_liked = db.session.query(VideoLike.query.filter_by(user_unique_id=user_id, video_unique_id=video_id).exists()).scalar()
        is_wished = db.session.query(VideoWish.query.filter_by(user_unique_id=user_id, video_unique_id=video_id).exists()).scalar()

    # 🔥 [2] 에피소드 로직 (시리즈물 전용)
    episodes = []
    if not video.video_is_movie:
        # 제목의 첫 단어로 같은 시리즈의 다른 회차들을 검색
        series_keyword = video.video_title.split(' ')[0]
        episodes = Video.query.filter(
            Video.video_is_movie == False,
            Video.video_title.like(f"%{series_keyword}%"),
            Video.video_unique_id != video_id
        ).order_by(Video.video_title.asc()).all()

    # 🔥 [3] 추천 콘텐츠 로직 (영화/시리즈 공통)
    # 현재 영상의 첫 번째 장르를 기준으로 검색
    primary_genre = video.video_genres.split(',')[0].strip() if video.video_genres else ""
    recommended_videos = Video.query.filter(
        Video.video_genres.like(f"%{primary_genre}%"),
        Video.video_unique_id != video_id
    ).limit(10).all()

    # 만약 장르 기반 추천이 없으면 최신 컨텐츠 10개 출력 (유지)
    if not recommended_videos:
        recommended_videos = Video.query.filter(
            Video.video_unique_id != video_id
        ).order_by(Video.video_date.desc()).limit(10).all()

    # [4] 평균 별점 계산
    avg_rating = round(sum(r.rating for r in all_reviews) / len(all_reviews), 1) if all_reviews else 0.0

    return render_template('sub/sub.html',
                           video=video,
                           user=user_data,
                           user_id=user_id,
                           history=history,
                           is_liked=is_liked,
                           is_wished=is_wished,
                           episodes=episodes,              # 💡 에피소드 리스트
                           recommended_videos=recommended_videos, # 💡 추천 리스트
                           avg_rating=avg_rating,
                           reviews=sorted_reviews,
                           review_count=len(sorted_reviews))
# 찜(Wish) 토글 API
@bp.route('/wish/<int:video_id>', methods=['POST'])
def toggle_wish(video_id):
    user_id = session.get('user')
    if not user_id: return jsonify({'msg': '로그인이 필요합니다.'}), 401

    wish = VideoWish.query.filter_by(user_unique_id=user_id, video_unique_id=video_id).first()
    if wish:
        db.session.delete(wish)
        status = False
    else:
        new_wish = VideoWish(user_unique_id=user_id, video_unique_id=video_id)
        db.session.add(new_wish)
        status = True
    db.session.commit()
    return jsonify({'is_wished': status})


# 시청 기록 저장 API
@bp.route('/save_watch', methods=['POST'])
def save_watch():
    user_id = session.get('user')
    if not user_id:
        return jsonify({'msg': 'skip'}), 200

    data = request.json
    # JS에서 보낸 키값 'video_id'와 'current_time'을 확인
    video_id = data.get('video_id')

    # 💡 데이터가 '{{...}}' 같은 문자열로 올 경우를 대비한 안전장치
    try:
        video_id = int(video_id)
    except (ValueError, TypeError):
        return jsonify({'msg': 'invalid video_id'}), 400

    # 소수점 시간을 정수로 변환 (예: 12.7초 -> 12초)
    current_time = int(float(data.get('current_time', 0)))
    is_finished = data.get('is_finished', False)

    # 기존 기록 찾기
    history = WatchHistory.query.filter_by(user_unique_id=user_id, video_unique_id=video_id).first()

    if not history:
        # 기록이 없으면 새로 생성
        history = WatchHistory(user_unique_id=user_id, video_unique_id=video_id)
        db.session.add(history)

    # 💡 값 업데이트
    history.last_played_time = current_time
    history.is_finished = is_finished
    history.updated_at = datetime.now(timezone.utc)  # 시청 시간 갱신

    db.session.commit()
    return jsonify({'msg': 'ok', 'saved_time': current_time})

@bp.route('/review/<int:video_id>', methods=['POST'])
def submit_review(video_id):
    user_id = session.get('user')
    if not user_id:
        return jsonify({'result': 'fail', 'message': '로그인이 필요합니다.'}), 401

    data = request.get_json()
    comment = data.get('comment')
    rating = data.get('rating')

    if not comment:
        return jsonify({'result': 'fail', 'message': '내용을 입력해주세요.'}), 400

    try:
        new_review = Review(
            user_unique_id=user_id,
            video_unique_id=video_id,
            comment=comment,
            rating=rating,
            create_at=datetime.now(timezone.utc)
        )
        db.session.add(new_review)
        db.session.commit()
        return jsonify({'result': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'result': 'fail', 'message': str(e)}), 500