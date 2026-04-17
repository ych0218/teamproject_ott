// 문서가 완전히 로드된 후 실행
document.addEventListener('DOMContentLoaded', function() {


    // 2. 비밀번호 실시간 입력 감지 -> 버튼 활성화
    const currentPw = document.getElementById('current_pw');
    const saveBtn = document.getElementById('save_btn');
    const pwMsg = document.getElementById('pw_msg');

    if (currentPw && saveBtn) {
        currentPw.addEventListener('input', function() {
            if (this.value.trim().length >= 4) {
                saveBtn.disabled = false;
                if (pwMsg) {
                    pwMsg.textContent = "정보를 저장할 준비가 되었습니다.";
                    pwMsg.style.color = "#4caf50";
                }
            } else {
                saveBtn.disabled = true;
                if (pwMsg) {
                    pwMsg.textContent = "정보 수정을 위해 현재 비밀번호를 입력해 주세요.";
                    pwMsg.style.color = "#666";
                }
            }
        });
    }

    // 3. 기존 버튼 클래스 교체 및 탭 로직
    const btns = document.querySelectorAll('.mypage_btn');
    btns.forEach(btn => {
        btn.classList.replace('mypage_btn', 'btn-chk');
    });

    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(button => {
        button.addEventListener('click', () => {
            const target = button.getAttribute('data-target');

            // 모든 버튼 active 제거
            tabBtns.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            // 모든 섹션 숨김 후 타겟 표시
            const sections = document.querySelectorAll('.tab-section');
            sections.forEach(section => section.classList.remove('active'));

            const targetSection = document.getElementById(target);
            if (targetSection) targetSection.classList.add('active');
        });
    });
});