document.addEventListener('DOMContentLoaded', function() {
    console.log("계정 통합 JS 로드 완료");

    const form = document.querySelector('.edit-form');
    const pw1 = document.getElementById('pw1');
    const pw2 = document.getElementById('pw2');
    const pwMsg = document.getElementById('pw_msg'); // 일치 메시지용
    const errorEl = document.getElementById("pw-error"); // 강도 메시지용
    const bar = document.getElementById("pw-strength-bar");
    const pwBarWrap = document.querySelector(".pw-bar");
    const saveBtn = document.getElementById('save_btn');

    const userEmail = saveBtn.dataset.email;

    // 1. 비밀번호 조건 검사 함수
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
                errorEl.textContent = "10자 이상+대소문자+숫자+특수문자 필수";
                errorEl.style.color = "#ff4d4d";
            } else {
                errorEl.textContent = "안전한 비밀번호입니다.";
                errorEl.style.color = "#00ff9d";
            }
        }
        return score === 5; // 모든 조건 충족 여부 반환
    }

    // 3. 메인 유효성 검사
    function validate() {
        const val1 = pw1.value;
        const val2 = pw2.value;

        // 비밀번호 강도 조건 확인
        const isStrengthOk = updateStrengthUI(val1);

        // 비밀번호 일치 확인
        let isMatch = false;
        if (val2.length > 0) {
            isMatch = (val1 === val2);
            pwMsg.textContent = isMatch ? "비밀번호가 일치합니다." : "비밀번호가 일치하지 않습니다.";
            pwMsg.style.color = isMatch ? "#00ff9d" : "#ff4d4d";
        } else {
            pwMsg.textContent = "";
        }

        // 이메일과 동일 여부
        const isNotEmail = (val1 !== userEmail);
        if (!isNotEmail && val1.length > 0) {
            errorEl.textContent = "이메일과 동일한 비밀번호는 불가합니다.";
            errorEl.style.color = "#ff4d4d";
        }

        // 전체 폼 유효성 (이름, 전화번호 등 필수값 체크)
        const isFormValid = form.checkValidity();

        // 최종 버튼 활성화: 강도OK + 일치OK + 이메일중복X + 폼전체OK
        saveBtn.disabled = !(isStrengthOk && isMatch && isNotEmail && isFormValid);
    }

    // 성별 버튼 및 모든 입력 이벤트 연결
    const genderLabels = document.querySelectorAll('.gender-btn');
    genderLabels.forEach(label => {
        label.addEventListener('click', function() {
            genderLabels.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            validate();
        });
    });

    form.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', validate);
    });

    validate();
});