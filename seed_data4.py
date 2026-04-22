from datetime import date
from one import create_app, db
from one.models import Video

def seed_data():
    print("-> 데이터를 업데이트합니다 (파일 경로는 유지됩니다)...")

    video_data = [
        {"id": 1, "title": "꾼", "director": "장창원", "actor": "현빈, 유지태, 나나", "date": date(2017, 11, 22), "genre": "범죄", "age": "15세", "desc": "희대의 사기꾼을 잡기 위해 사기꾼들이 뭉쳤다! 엘리트 검사와 사기꾼들의 예측불가 팀플레이."},
        {"id": 2, "title": "괴물", "director": "봉준호", "actor": "송강호, 변희봉, 박해일, 배두나", "date": date(2006, 7, 27), "genre": "스릴러, SF, 가족", "age": "12세", "desc": "햇살 가득한 한강 둔치, 정체불명의 괴물이 나타나 딸 현서를 낚아채 간다! 평범한 가족의 사투가 시작된다."},
        {"id": 3, "title": "바람", "director": "이성한", "actor": "정우, 황정음", "date": date(2009, 11, 26), "genre": "드라마, 액션", "age": "15세", "desc": "폼 나고만 싶었던 부산의 고등학생 짱구의 파란만장한 성장통을 그린 이야기."},
        {"id": 4, "title": "베테랑", "director": "류승완", "actor": "황정민, 유아인", "date": date(2015, 8, 5), "genre": "액션, 범죄", "age": "15세", "desc": "한 번 꽂힌 놈은 끝까지 잡는 베테랑 광수대 서도철과 안하무인 재벌 3세의 정면 승부."},
        {"id": 5, "title": "타짜: 신의 손", "director": "강형철", "actor": "T.O.P, 신세경", "date": date(2014, 9, 3), "genre": "범죄, 드라마", "age": "청불", "desc": "삼촌 고니를 닮아 어린 시절부터 남다른 손재주를 보인 대길이 타짜 세계에 뛰어든다."},
        {"id": 6, "title": "두사부일체", "director": "윤제균", "actor": "정준호, 정웅인", "date": date(2001, 12, 8), "genre": "코미디, 액션", "age": "18세", "desc": "조직의 보스가 고등학교 졸업장을 따기 위해 학교로 돌아가며 벌어지는 좌충우돌 코미디."},
        {"id": 7, "title": "올드보이", "director": "박찬욱", "actor": "최민식, 유지태", "date": date(2003, 11, 21), "genre": "스릴러, 미스터리", "age": "청불", "desc": "15년간 영문도 모른 채 갇혀 지낸 오대수가 풀려난 뒤 범인을 찾기 위한 처절한 복수."},
        {"id": 8, "title": "아가씨", "director": "박찬욱", "actor": "김민희, 김태리, 하정우", "date": date(2016, 6, 1), "genre": "드라마, 스릴러", "age": "청불", "desc": "막대한 재산을 상속받게 된 귀족 아가씨와 그녀를 속이려는 하녀, 백작의 매혹적인 이야기."},
        {"id": 9, "title": "친구 2", "director": "곽경택", "actor": "유오성, 김우빈", "date": date(2013, 11, 14), "genre": "범죄, 액션", "age": "청불", "desc": "친구 동수의 죽음 이후 17년 뒤, 감옥에서 나온 준석이 동수의 아들 성훈을 만나며 벌어지는 일."},
        {"id": 10, "title": "암살", "director": "최동훈", "actor": "전지현, 이정재, 하정우", "date": date(2015, 7, 22), "genre": "액션, 드라마", "age": "15세", "desc": "1933년 조국이 사라진 시대, 친일파 암살 작전을 둘러싼 독립군들과 밀정의 선택."},
        {"id": 11, "title": "범죄와의 전쟁", "director": "윤종빈", "actor": "최민식, 하정우", "date": date(2012, 2, 2), "genre": "범죄, 드라마", "age": "청불", "desc": "1980년대 부산, 비리 세관원 출신 최익현과 조폭 보스 최형배의 나쁜 놈들 전성시대."},
        {"id": 12, "title": "극한직업", "director": "이병헌", "actor": "류승룡, 이하늬", "date": date(2019, 1, 23), "genre": "코미디, 액션", "age": "15세", "desc": "낮에는 치킨장사, 밤에는 잠복근무. 마약반 5인방의 위장 창업 수사극."},
        {"id": 13, "title": "애니멀 킹덤", "director": "토마 카예", "actor": "로망 뒤리스", "date": date(2024, 3, 20), "genre": "어드벤처, 드라마", "age": "12세", "desc": "인간이 동물로 변해가는 기이한 현상이 퍼지는 세상, 아내를 찾기 위한 부자의 여정."},
        {"id": 14, "title": "언터처블: 1%의 우정", "director": "올리비에 나카체", "actor": "프랑수아 클루제, 오마 사이", "date": date(2012, 3, 22), "genre": "드라마, 코미디", "age": "12세", "desc": "전신마비 백만장자와 무일푼 백수가 만나 펼치는 세상 1%의 특별한 우정."},
        {"id": 15, "title": "F1, 본능의 질주", "director": "제임스 게이 리스", "actor": "루이스 해밀턴", "date": date(2024, 2, 23), "genre": "다큐멘터리", "age": "12세", "desc": "세계 최고의 속도를 겨루는 F1 서킷 안팎에서 벌어지는 드라이버들의 치열한 생존 경쟁."},
        {"id": 16, "title": "놀면 뭐하니?", "director": "김진용, 장우성", "actor": "유재석, 하하, 주우재", "date": date(2019, 7, 27), "genre": "예능", "age": "15세", "desc": "유재석에게 맡긴 릴레이 카메라로 시작된 예상치 못한 확장! 다양한 프로젝트로 웃음을 선사하는 버라이어티."},
        {"id": 17, "title": "냉장고를 부탁해", "director": "이창우", "actor": "김성주, 안정환", "date": date(2014, 11, 17), "genre": "예능, 요리", "age": "15세", "desc": "스타의 냉장고를 직접 스튜디오로! 대한민국 최고의 셰프들이 15분 만에 펼치는 기막힌 요리 대결."},
        {"id": 18, "title": "나 혼자 산다", "director": "허항", "actor": "전현무, 박나래, 기안84", "date": date(2013, 3, 22), "genre": "예능, 관찰", "age": "15세", "desc": "1인 가구 전성시대! 혼자 사는 연예인들의 진솔하고 유쾌한 일상을 담은 관찰 예능 프로그램."},
        {"id": 19, "title": "벌거벗은 세계사", "director": "김형오", "actor": "은지원, 규현, 이혜성", "date": date(2020, 12, 12), "genre": "예능, 교양", "age": "12세", "desc": "전 세계 곳곳을 온택트로 둘러보며 각 나라의 명소와 역사를 파헤치는 언택트 세계사 강의."},
        {"id": 20, "title": "오은영 리포트 - 결혼 지옥", "director": "정윤정", "actor": "오은영, 소유진, 김응수", "date": date(2022, 5, 16), "genre": "예능, 상담", "age": "15세", "desc": "어느새 남보다 못한 사이가 된 부부들의 일상을 관찰하고, 국민 멘토 오은영 박사가 직접 솔루션을 제시한다."},
        {"id": 21, "title": "하트시그널 4", "director": "박철환", "actor": "신민규, 한겨레, 유지원, 이후신, 이주미, 김지영, 김지민, 유이수", "date": date(2023, 5, 17), "genre": "예능, 연애", "age": "15세", "desc": "시그널 하우스에 입주하게 된 청춘 남녀들의 짜릿한 동거! 무의식중에 나타나는 하트시그널을 찾아내며 진정한 사랑을 추리하는 연애 리얼리티."},
        {"id": 22, "title": "이혼숙려캠프", "director": "김민종", "actor": "박하선, 서장훈", "date": date(2024, 4, 4), "genre": "예능, 상담", "age": "15세", "desc": "위기의 부부들이 합숙을 통해 관계를 돌아보는 리얼 상담 예능."},
        {"id": 23, "title": "아는 형님", "director": "최창수", "actor": "강호동, 서장훈, 김희철", "date": date(2015, 12, 5), "genre": "예능, 코미디", "age": "15세", "desc": "이성 상실, 본능 충실! 형님 학교에서 벌어지는 전학생들과의 케미."},
        {"id": 24, "title": "나는 SOLO", "director": "남규홍", "actor": "데프콘, 이이경, 송해나", "date": date(2021, 7, 14), "genre": "예능, 연애", "age": "15세", "desc": "결혼을 간절히 원하는 솔로 남녀들의 극사실주의 데이팅 프로그램."},
        {"id": 25, "title": "유 퀴즈 온 더 블럭", "director": "박근형", "actor": "유재석, 조세호", "date": date(2018, 8, 29), "genre": "예능, 토크", "age": "12세", "desc": "자기님들의 소박한 인생 이야기와 깜짝 퀴즈가 있는 사람 여행."},
        {"id": 26, "title": "지구오락실", "director": "나영석, 박현용", "actor": "이은지, 미미, 이영지, 안유진", "date": date(2022, 6, 24), "genre": "예능, 어드벤처", "age": "15세", "desc": "지구로 도망간 달나라 토끼를 잡기 위해 뭉친 4명의 용사들! 시공간을 넘나들며 펼쳐지는 신개념 하이브리드 멀티버스 액션 예능."},
        {"id": 27, "title": "놀라운 토요일", "director": "이태경", "actor": "신동엽, 김동현, 문세윤, 박나래, 한해, 키, 붐, 입짧은햇님, 피오, 태연", "date": date(2018, 4, 7), "genre": "예능, 음악", "age": "12세", "desc": "전국 시장의 핫한 음식을 걸고 벌이는 노래 가사 받아쓰기 게임! 받아쓰기에 진심인 멤버들의 좌충우돌 도레미 마켓."},
        {"id": 28, "title": "맛있는 녀석들", "director": "이명규", "actor": "김준현, 문세윤, 황제성, 김해준", "date": date(2015, 1, 30), "genre": "예능, 먹방", "age": "12세", "desc": "먹어본 자가 맛을 안다! 단순한 먹방을 넘어 음식을 더 맛있게 즐기는 팁을 제안하는 본격 먹방 프로그램."},
        {"id": 29, "title": "구해줘! 홈즈", "director": "정다히", "actor": "김숙, 박나래, 양세형, 장동민, 양세찬", "date": date(2019, 2, 4), "genre": "예능, 리얼리티", "age": "15세", "desc": "바쁜 현대인들을 대신해 직접 발품을 팔아 집을 찾아주는 중개 배틀! 실속 있는 정보와 다양한 주거 형태를 소개."},
        {"id": 30, "title": "삼시세끼 어촌편 5", "director": "나영석, 이진주", "actor": "차승원, 유해진, 손호준", "date": date(2020, 5, 1), "genre": "예능, 야외", "age": "15세", "desc": "도시를 떠나 낯선 섬마을에서 자급자족하며 끼니를 해결하는 힐링 예능. '차줌마'와 '참바다'의 완벽한 케미스트리."},
        {"id": 31, "title": "환승연애 4", "director": "김인하", "actor": "홍지연, 김우진, 정원규, 박지현, 성백현, 최윤영, 조유식, 박현지 등", "date": date(2025, 10, 1), "genre": "예능, 연애", "age": "15세", "desc": "누구보다 잘 알았던 'X'와 설레는 'NEW' 사이, 다시 사랑할 수 있을까? 이전 시즌보다 빠른 전개와 '타임룸' 등 새로운 장치로 몰입감을 더한 환승연애의 네 번째 여정."},
    ]

    try:
        for item in video_data:
            # 1. 이미 DB에 해당 영화가 있는지 ID로 찾습니다.
            existing_video = Video.query.filter_by(video_unique_id=item["id"]).first()

            if existing_video:
                # 2. 이미 있다면, 상세 정보만 업데이트 (Thumbnail, URL은 수정 안 함)
                existing_video.video_title = item["title"]
                existing_video.video_director = item["director"]
                existing_video.video_actor = item["actor"]
                existing_video.video_age_limit = item["age"]
                existing_video.video_date = item["date"]
                existing_video.video_synopsis = item["desc"]
                existing_video.video_genres = item["genre"]
                print(f"   - [{item['title']}] 정보 업데이트 완료")
            else:
                # 3. DB에 없다면 새로 생성 (이때만 기본 경로 사용)
                new_v = Video(
                    video_unique_id=item["id"],
                    video_title=item["title"],
                    video_director=item["director"],
                    video_actor=item["actor"],
                    video_age_limit=item["age"],
                    video_date=item["date"],
                    video_synopsis=item["desc"],
                    video_genres=item["genre"],
                    video_is_movie=0 if item["id"] >= 16 else 1, # 16번부터는 예능(0)으로 설정
                    video_url=f"/static/uploads/videos/video_{item['id']}.mp4",
                    video_thumbnail=f"/static/uploads/thumbnails/thumb_{item['id']}.jpg",
                    admin_unique_id=1
                )
                db.session.add(new_v)
                print(f"   - [{item['title']}] 새로 추가됨")
        
        db.session.commit()
        print("✅ 업데이트가 완료되었습니다!")

    except Exception as e:
        db.session.rollback()
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_data()