let fixedRating = 0;
document.addEventListener('DOMContentLoaded', function () {
    // 1. URL에서 어떤 탭을 열어야 하는지 파라미터 확인 (?tab=tab1)
    const urlParams = new URLSearchParams(window.location.search);
    const activeTab = urlParams.get('tab');

    // 2. 만약 리뷰 등록 후 넘어왔다면 해당 탭 강제 클릭
    if (activeTab) {
        const targetBtn = document.querySelector(`.tab-link[onclick*='${activeTab}']`);
        if (targetBtn) {
            targetBtn.click(); // 기존에 만든 openTab 함수를 실행시킵니다.
        }
    }
    // 1. 별점 이벤트 연결
    const starElements = document.querySelectorAll('.comments .star');
    starElements.forEach((star) => {
        star.addEventListener('mouseenter', () => renderStars(parseFloat(star.getAttribute('data-value'))));
        star.addEventListener('mouseleave', () => renderStars(fixedRating));
        star.addEventListener('click', () => {
            fixedRating = parseFloat(star.getAttribute('data-value'));
            renderStars(fixedRating);
        });
    });
});

/* [기능] 별점 UI 업데이트 */
function renderStars(rating) {
    const stars = document.querySelectorAll('.comments .star');
    stars.forEach((star) => {
        const val = parseFloat(star.getAttribute('data-value'));
        if (val <= rating) {
            star.classList.add('fill');
        } else {
            star.classList.remove('fill');
        }
    });
}

/* [기능] 탭 전환 */
window.openTab = function (evt, tabName) {
    const tabContents = document.querySelectorAll(".tab-content");
    const tabLinks = document.querySelectorAll(".tab-link");

    tabContents.forEach(content => {
        content.style.display = "none";
        content.classList.remove("active");
    });
    tabLinks.forEach(link => link.classList.remove("active"));

    const targetTab = document.getElementById(tabName);
    if (targetTab) {
        targetTab.style.display = "block";
        targetTab.classList.add("active");
    }
    evt.currentTarget.classList.add("active");
};

/* [기능] 리뷰 제출 */
window.submitReview = function (videoId) {
    const submitBtn = document.getElementById('submit-btn');
    const commentInput = document.getElementById('comment-text');
    const text = commentInput.value.trim();

    // 💡 [추가] 시청 여부 체크 (HTML에서 window.VIDEO_DATA에 시청 여부를 담았을 경우)
    // 혹은 단순히 서버의 에러 메시지에 의존해도 충분합니다.

    if (submitBtn.innerText !== "수정 완료") {
        const alreadyExists = document.querySelector('.comment-card.is-me');
        if (alreadyExists) {
            alert("이미 리뷰를 작성하셨습니다. 수정 기능을 이용해주세요!");
            return;
        }
    }

    if (fixedRating === 0) return alert("별점을 선택해주세요!");
    if (!text) return alert("후기 내용을 입력해주세요.");

    fetch(`/video/review/${videoId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment: text, rating: fixedRating })
    })
    .then(res => res.json())
    .then(data => {
        if (data.result === 'success') {
            location.href = window.location.pathname + '?tab=tab1';
        } else {
            // 💡 여기서 서버가 보낸 "영상을 시청한 분들만..." 메시지가 출력됩니다.
            alert(data.message);
        }
    });
};

/* [기능] 찜하기 */
window.toggleWish = function (videoId) {
    fetch(`/video/wish/${videoId}`, { method: 'POST' })
    .then(res => res.json())
    .then(data => {
        const icon = document.getElementById("wishIcon");
        const path = "/static/img/main_img/";
        icon.src = data.is_wished ? path + "icon-heart-filled.svg" : path + "icon-heart-outlined.svg";
        
        const toast = document.getElementById("toast1");
        document.getElementById("toast1Text").innerText = data.is_wished ? "찜 목록에 추가되었습니다!" : "찜이 취소되었습니다.";
        toast.classList.add("show");
        setTimeout(() => toast.classList.remove("show"), 3000);
    });
};

/* [기능] 공유하기 */
window.copyLink = function () {
    navigator.clipboard.writeText(window.location.href).then(() => {
        const toast = document.getElementById("toast");
        toast.classList.add("show");
        setTimeout(() => toast.classList.remove("show"), 3000);
    });
};


let watchTimer;

/* [기능] 비디오 재생 및 이벤트 바인딩 */
window.playVideo = function(videoId) {



    const videoElement = document.getElementById('mainVideo');
    const thumbLayer = document.getElementById('thumbnailLayer');
    const resumeModal = document.getElementById('resumeModal');
    // 💡 HTML에서 넘겨준 can_watch 변수를 전역에서 확인 (또는 간단하게 처리)
    // 현재는 HTML 레벨에서 onclick 자체를 막았으므로 실행되지 않겠지만, 추가 안전장치입니다.
    if (typeof can_watch !== 'undefined' && !can_watch) {
        alert("구독권이 필요합니다.");
        return;
    }
    // 1. UI 전환
    if (thumbLayer) thumbLayer.style.display = 'none';
    if (videoElement) videoElement.style.display = 'block';

    const lastTime = window.VIDEO_DATA ? window.VIDEO_DATA.lastTime : 0;
    console.log("현재 체크 중인 시간:", lastTime); // 👈 이거 추가
    // 2. 10초 이상 시청 기록이 있을 경우 모달 표시
    if (lastTime > 0) {
    console.log("모달을 띄워야 함!");
        resumeModal.style.display = 'flex'; // 모달 띄우기

        // [이어서 보기 클릭]
        document.getElementById('btnResume').onclick = function() {
            resumeModal.style.display = 'none';
            videoElement.currentTime = lastTime;
            videoElement.play();
            startWatchTimer(videoId, videoElement);
        };

        // [처음부터 보기 클릭]
        document.getElementById('btnStartOver').onclick = function() {
            resumeModal.style.display = 'none';
            videoElement.currentTime = 0;
            videoElement.play();
            startWatchTimer(videoId, videoElement);
            // 0초부터 보는 것이니 DB도 즉시 갱신해주는 것이 좋습니다.
            saveWatchProgress(videoId, 0, false);
        };
    } else {
        // 기록 없으면 즉시 재생
        videoElement.play();
        startWatchTimer(videoId, videoElement);
    }

    // 시간 이동 및 일시정지 이벤트 바인딩
    videoElement.onseeked = () => saveWatchProgress(videoId, videoElement.currentTime, false);
    videoElement.onpause = () => saveWatchProgress(videoId, videoElement.currentTime, false);
};

/* [기능] 타이머 관리 */
function startWatchTimer(videoId, videoElement) {
    if (window.watchTimer) clearInterval(window.watchTimer);

    // 💡 즉시 저장
    saveWatchProgress(videoId, videoElement.currentTime, false);

    window.watchTimer = setInterval(() => {
        // 재생 중일 때만 주기적으로 저장
        if (videoElement && !videoElement.paused) {
            saveWatchProgress(videoId, videoElement.currentTime, false);
        }
    }, 10000);
}

// 페이지를 떠날 때 최종 저장
window.addEventListener('beforeunload', () => {
    const videoElement = document.getElementById('mainVideo');
    // 💡 HTML에서 정의한 전역 변수에서 ID 가져오기
    const videoId = window.VIDEO_DATA ? window.VIDEO_DATA.id : null;

    if (videoId && videoElement && !videoElement.paused) {
        saveWatchProgress(videoId, videoElement.currentTime, false);
    }
});


function saveWatchProgress(videoId, currentTime, isFinished) {
    // 1. 전달받은 ID가 없으면 전역 객체에서 보충
    const rawId = videoId || (window.VIDEO_DATA ? window.VIDEO_DATA.id : null);

    // 2. 숫자로 명확히 변환 (비어있거나 숫자가 아니면 중단)
    const finalId = parseInt(rawId);
    if (isNaN(finalId)) {
        console.error("비디오 ID가 유효하지 않습니다:", rawId);
        return;
    }

    // 3. 서버 전송
    fetch('/video/save_watch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            video_id: finalId, // 명확한 숫자형 전송
            current_time: Math.floor(currentTime),
            is_finished: isFinished
        })
    })
    .then(res => res.json())
    .then(data => console.log("저장 결과:", data)) // 결과 로그 확인용
    .catch(err => console.error("전송 에러:", err));
}

window.toggleAudio = function() {
    const video = document.getElementById('mainVideo');
    const icon = document.getElementById('volIcon');

    // 소리 켜기/끄기 토글
    video.muted = !video.muted;

    // 아이콘 변경
    if (video.muted) {
        icon.src = "/static/img/main_img/volume_off.svg";
    } else {
        icon.src = "/static/img/main_img/volume_up.svg";
    }
};

window.prepareEdit = function(content, rating) {
    const inputArea = document.getElementById('reviewInputArea');
    const msgArea = document.querySelector('.already-reviewed-msg');

    // 1. 여기서 변수를 'commentInput'이라는 이름으로 선언합니다.
    const commentInput = document.getElementById('comment-text');

    // 2. 입력창 영역 보이기 처리
    if(inputArea) inputArea.style.display = 'block';
    if(msgArea) msgArea.style.display = 'none';

    // 3. 선언한 commentInput 변수를 사용하여 값을 채웁니다.
    if (commentInput) {
        commentInput.value = content;
        commentInput.focus();
    }

    // 4. 별점 세팅
    fixedRating = parseInt(rating);
    renderStars(fixedRating);

    // 5. 버튼 텍스트 변경
    const submitBtn = document.getElementById('submit-btn');
    if (submitBtn) submitBtn.innerText = "수정 완료";
};

/* [기능] 리뷰 삭제 */
window.deleteReview = function(videoId) {
    if (!confirm("작성하신 리뷰를 정말 삭제하시겠습니까?")) return;

    fetch(`/video/review_delete/${videoId}`, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        if (data.result === 'success') {
            location.href = window.location.pathname + '?tab=tab1';
        } else {
            alert(data.message);
        }
    });
};