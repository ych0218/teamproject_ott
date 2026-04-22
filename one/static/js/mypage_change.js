document.addEventListener('DOMContentLoaded', function() {
    console.log("마이페이지 수정 JS 로드 완료");

    const currentPw = document.getElementById('current_pw');
    const newPw = document.getElementById('new_pw');
    const confirmPw = document.getElementById('confirm_pw');
    const saveBtn = document.getElementById('save_btn');

    // UI 요소들 (메시지 및 게이지)
    const errorEl = document.getElementById("pw-error");
    const matchMsg = document.getElementById("match_msg");
    const bar = document.getElementById("pw-strength-bar");
    const pwBarWrap = document.querySelector(".pw-bar");

    // 버튼에 심어둔 정보 가져오기
    const signupMethod = saveBtn.dataset.method; // HTML에서 data-method="{{ user.signup_method }}"

    // 1. 비밀번호 조건 검사 함수 (회원가입과 동일)
    function getPasswordStatus(pw) {
        return {
            lengthOk: pw.length >= 10,
            upperOk: /[A-Z]/.test(pw),
            lowerOk: /[a-z]/.test(pw),
            numOk: /[0-9]/.test(pw),
            specialOk: /[^A-Za-z0-9]/.test(pw)
        };
    }

    // 2. 강도 체크 UI 업데이트
    function updateStrengthUI(pw) {
        if (pwBarWrap) {
            pw ? pwBarWrap.classList.add("active") : pwBarWrap.classList.remove("active");
        }

        if (!pw) {
            if (errorEl) errorEl.textContent = "";
            if (bar) bar.style.width = "0%";
            return;
        }

        const v = getPasswordStatus(pw);
        let score = 0;
        if (v.lengthOk) score++;
        if (v.upperOk) score++;
        if (v.lowerOk) score++;
        if (v.numOk) score++;
        if (v.specialOk) score++;

        if (bar) {
            bar.style.width = (score * 20) + "%";
            if (score <= 2) bar.style.backgroundColor = "#ff4d4d";
            else if (score === 3) bar.style.backgroundColor = "#ffa500";
            else if (score === 4) bar.style.backgroundColor = "#00c853";
            else if (score === 5) bar.style.backgroundColor = "#00ff9d";
        }

        if (errorEl) {
            if (score < 5) {
                errorEl.textContent = "보안 등급 낮음 (10자 이상+대소문자+숫자+특수문자)";
                errorEl.style.color = "#ff4d4d";
            } else {
                errorEl.textContent = "안전한 비밀번호입니다.";
                errorEl.style.color = "#00ff9d";
            }
        }
    }

    // 3. 메인 유효성 검사 (버튼 활성화 결정)
    function validate() {
        const currVal = currentPw.value.trim();
        const newVal = newPw.value.trim();
        const cfmVal = confirmPw.value.trim();

        // 현재 비밀번호 체크: 소셜 유저는 무조건 통과, 일반 유저는 1글자라도 입력해야 함
        const isCurrentOk = (signupMethod !== 'email') ? true : currVal.length > 0;

        let isNewOk = true;

        // 새 비밀번호를 입력하려는 경우
        if (newVal.length > 0) {
            const v = getPasswordStatus(newVal);
            const isStrengthOk = v.lengthOk && v.upperOk && v.lowerOk && v.numOk && v.specialOk;
            const isMatch = (newVal === cfmVal);

            // 일치 메시지 업데이트
            if (cfmVal.length > 0) {
                matchMsg.textContent = isMatch ? "비밀번호가 일치합니다." : "비밀번호가 서로 다릅니다.";
                matchMsg.style.color = isMatch ? "#00ff9d" : "#ff4d4d";
            } else {
                matchMsg.textContent = "";
            }

            isNewOk = isStrengthOk && isMatch;
        } else {
            // 새 비밀번호를 입력 안 하는 경우 (메시지 초기화)
            matchMsg.textContent = "";
            if (errorEl) errorEl.textContent = "";
            if (bar) bar.style.width = "0%";
        }

        // 최종 버튼 활성화
        saveBtn.disabled = !(isCurrentOk && isNewOk);
    }

    // 이벤트 리스너 등록
    [currentPw, newPw, confirmPw].forEach(el => {
        if (el) {
            el.addEventListener('input', () => {
                if (el === newPw) updateStrengthUI(newPw.value);
                validate();
            });
        }
    });
});