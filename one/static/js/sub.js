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
    const commentInput = document.getElementById('comment-text');
    const text = commentInput.value.trim();

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
            // 🔥 핵심: 그냥 reload가 아니라 탭 정보를 주소에 붙여서 이동
            location.href = window.location.pathname + '?tab=tab1';
        } else {
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

window.playVideo = function(videoId) {
    const videoElement = document.getElementById('mainVideo');
    const thumbLayer = document.getElementById('thumbnailLayer');

    // 1. DB에서 가져온 마지막 시청 시간 (이미 전역변수에 담겨 있음)
    const lastTime = window.VIDEO_DATA ? window.VIDEO_DATA.lastTime : 0;

    // 2. UI 화면 전환
    if (thumbLayer) thumbLayer.style.display = 'none';
    if (videoElement) videoElement.style.display = 'block';

    // 3. 💡 핵심 로직: 영상 로드 후 시간 이동 함수
    const seekAndPlay = () => {
        // 이벤트를 한 번만 실행하기 위해 제거
        videoElement.onloadedmetadata = null;

        if (lastTime > 0) {
            console.log(`DB 기록 확인: ${lastTime}초 지점으로 이동합니다.`);
            videoElement.currentTime = lastTime; // 👈 보던 시간으로 타임라인 이동
        }

        videoElement.play(); // 이동 후 재생 시작
    };

    // 4. 영상 정보 로드 상태 체크
    if (videoElement.readyState >= 1) {
        // 이미 메타데이터(길이 등)가 로드된 경우 즉시 실행
        seekAndPlay();
    } else {
        // 아직 로드 전이라면 로드 완료 신호(onloadedmetadata)를 기다림
        videoElement.onloadedmetadata = seekAndPlay;
    }

    // 5. 시청 기록 저장 타이머 시작 (기존 로직)
    startWatchTimer(videoId, videoElement);
};

// [유틸] 타이머 관리 함수 (깔끔하게 분리)
function startWatchTimer(videoId, videoElement) {
    if (window.watchTimer) clearInterval(window.watchTimer);
    window.watchTimer = setInterval(() => {
        if (!videoElement.paused) {
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
    // 💡 매개변수로 넘어온 videoId가 없으면 전역 변수에서 가져옴
    const finalId = videoId || (window.VIDEO_DATA ? window.VIDEO_DATA.id : null);

    if (!finalId || isNaN(finalId)) {
        console.error("정상적인 비디오 ID가 아닙니다:", finalId);
        return;
    }

    fetch('/video/save_watch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            video_id: finalId,
            current_time: Math.floor(currentTime),
            is_finished: isFinished
        })
    });
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