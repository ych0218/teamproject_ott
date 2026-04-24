from flask import Blueprint, render_template, session, jsonify, request
from ..models import Video, User, WatchHistory, VideoLike, VideoWish, db, Review, Subscription
from datetime import datetime, timezone
from sqlalchemy import or_
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
    # [구독 체크 로직 추가]
    can_watch = False
    if user_id:
        now = datetime.now(timezone.utc)
        # 해당 유저의 구독 중 'active' 상태이고 종료일이 남은 기록이 있는지 확인
        active_sub = Subscription.query.filter_by(user_unique_id=user_id, status='active') \
            .filter(Subscription.end_date > now) \
            .first()

        if active_sub:
            can_watch = True



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
    series_keyword = video.video_title  # 1. 기본값으로 현재 제목 전체를 넣어둡니다 (에러 방지)


    if ' ' in video.video_title:
        series_keyword = video.video_title.split(' ')[0]
    episodes = Video.query.filter(
        Video.video_is_movie == False,
        Video.video_title.like(f"%{series_keyword}%"),
        Video.video_unique_id != video_id  # 현재 보고 있는 영상 제외
    ).order_by(Video.video_title.asc()).all()
    # --- 테스트 코드 시작 ---
    print("\n" + "=" * 50)
    print(f"📍 현재 영상 제목: {video.video_title} (ID: {video_id})")
    print(f"🔍 검색 키워드: {series_keyword}")

    # 전체 영상 중 제목에 키워드가 포함된 것들을 다 가져와서 비교해봅니다.
    all_related = Video.query.filter(Video.video_title.like(f"%{series_keyword}%")).all()

    print(f"📑 검색된 전체 관련 영상 ({len(all_related)}개):")
    for v in all_related:
        print(f"   - 제목: {v.video_title} / ID: {v.video_unique_id} / 시리즈여부(is_movie): {v.video_is_movie}")

    print(f"🎬 최종 필터링된 episodes 결과: {episodes}")
    print("=" * 50 + "\n")
    # --- 테스트 코드 끝 ---
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
                           can_watch=can_watch,
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
    # 1. 세션 값 확인 및 숫자 변환
    user_id_raw = session.get('user')
    if not user_id_raw:
        return jsonify({'msg': 'user session missing'}), 401

    try:
        user_id = int(user_id_raw)  # 세션값이 문자열일 경우 대비
        data = request.json

        # 2. 필수 데이터 추출 및 숫자 변환
        video_id = int(data.get('video_id'))
        current_time = int(float(data.get('current_time', 0)))
        is_finished = data.get('is_finished', False)

        # 3. DB 객체 조회 및 생성
        history = WatchHistory.query.filter_by(user_unique_id=user_id, video_unique_id=video_id).first()

        if not history:
            # 💡 새로 입력할 때 명시적으로 값 할당
            history = WatchHistory(
                user_unique_id=user_id,
                video_unique_id=video_id,
                last_played_time=current_time,
                is_finished=is_finished
            )
            db.session.add(history)
        else:
            # 💡 기존 기록 업데이트
            history.last_played_time = current_time
            history.is_finished = is_finished
            history.updated_at = datetime.now(timezone.utc)

        db.session.commit()  # 👈 최종 반영
        return jsonify({'msg': 'success', 'id': video_id})

    except Exception as e:
        db.session.rollback()
        print(f"❌ DB 입력 에러 발생: {str(e)}")  # 서버 터미널 로그를 확인하세요
        return jsonify({'msg': 'error', 'reason': str(e)}), 500


# 검색
@bp.route('/search')
def search():
    keyword = request.args.get('keyword', '').strip()

    query = Video.query

    if keyword:
        query = query.filter(Video.video_title.contains(keyword))

    video_list = query.order_by(Video.video_unique_id.desc()).all()

    return render_template('sub/search_result.html', video_list=video_list, keyword=keyword)

@bp.route('/review/<int:video_id>', methods=['POST'])
def submit_review(video_id):
    user_id = session.get('user')
    if not user_id:
        return jsonify({'result': 'fail', 'message': '로그인이 필요합니다.'}), 401

    data = request.get_json()
    comment = data.get('comment')
    rating = data.get('rating')
    # 💡 [핵심 추가] 시청 기록이 있는지 확인
    # 영상 재생 시 자동으로 생성되는 WatchHistory 테이블을 조회합니다.
    history = WatchHistory.query.filter_by(user_unique_id=user_id, video_unique_id=video_id).first()

    if not history:
        return jsonify({
            'result': 'fail',
            'message': '영상을 시청하신 분들만 리뷰를 작성할 수 있습니다.'
        }), 403  # Forbidden

    if not comment:
        return jsonify({'result': 'fail', 'message': '내용을 입력해주세요.'}), 400

    try:
        # 💡 기존 리뷰가 있는지 먼저 확인
        existing_review = Review.query.filter_by(user_unique_id=user_id, video_unique_id=video_id).first()

        if existing_review:
            # 기존 리뷰가 있다면 내용과 별점 업데이트
            existing_review.comment = comment
            existing_review.rating = rating
            existing_review.create_at = datetime.now(timezone.utc)
        else:
            # 없다면 새로 생성
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


@bp.route('/review_delete/<int:video_id>', methods=['POST'])
def delete_review(video_id):
    user_id = session.get('user')
    if not user_id:
        return jsonify({'result': 'fail', 'message': '로그인이 필요합니다.'}), 401

    try:
        # 내 아이디와 비디오 아이디가 일치하는 리뷰 찾기
        review = Review.query.filter_by(user_unique_id=user_id, video_unique_id=video_id).first()

        if review:
            db.session.delete(review)
            db.session.commit()
            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'fail', 'message': '삭제할 리뷰를 찾을 수 없습니다.'}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({'result': 'fail', 'message': str(e)}), 500