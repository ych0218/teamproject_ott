document.addEventListener("DOMContentLoaded", function () {

    // ===== 생년월일 =====
    const yearSelect = document.querySelector("[name='birth_year']");
    const monthSelect = document.querySelector("[name='birth_month']");
    const daySelect = document.querySelector("[name='birth_day']");

    if (yearSelect && monthSelect && daySelect) {

        const currentYear = new Date().getFullYear();

        yearSelect.innerHTML = '<option value="">년도</option>';
        monthSelect.innerHTML = '<option value="">월</option>';
        daySelect.innerHTML = '<option value="">일</option>';

        monthSelect.disabled = true;
        daySelect.disabled = true;

        for (let y = currentYear; y >= currentYear - 100; y--) {
            yearSelect.add(new Option(y + "년", y));
        }

        yearSelect.addEventListener("change", function () {
            const year = this.value;

            monthSelect.innerHTML = '<option value="">월</option>';
            daySelect.innerHTML = '<option value="">일</option>';
            daySelect.disabled = true;

            if (!year) {
                monthSelect.disabled = true;
                return;
            }

            monthSelect.disabled = false;

            for (let m = 1; m <= 12; m++) {
                monthSelect.add(new Option(m + "월", m));
            }
        });

        monthSelect.addEventListener("change", function () {
            const year = yearSelect.value;
            const month = this.value;

            daySelect.innerHTML = '<option value="">일</option>';

            if (!month) {
                daySelect.disabled = true;
                return;
            }

            daySelect.disabled = false;

            const lastDay = new Date(year, month, 0).getDate();

            for (let d = 1; d <= lastDay; d++) {
                daySelect.add(new Option(d + "일", d));
            }
        });
    }

    // ===== 성별 버튼 =====
    const buttons = document.querySelectorAll(".gender-btn");

    buttons.forEach(btn => {
        btn.addEventListener("click", function () {
            buttons.forEach(b => b.classList.remove("active"));
            this.classList.add("active");

            const radio = this.closest("label").querySelector("input");
            if (radio) radio.checked = true;
        });
    });

       // ===== 비밀번호 =====
    const password1 = document.getElementById("password1");
    const password2 = document.getElementById("password2");
    const errorEl = document.getElementById("pw-error");
    const matchMsg = document.getElementById("password-match-msg");
    const bar = document.getElementById("pw-strength-bar"); // ⭐ 추가

    if (password1 && password2) {

        function checkPasswordStrength() {
            const pw = password1.value;

            if (!pw) {
                errorEl.textContent = "";
                bar.style.width = "0%"; // ⭐ 초기화
                return;
            }

            let score = 0;

            const lengthOk = pw.length >= 10;
            const upperOk = /[A-Z]/.test(pw);
            const lowerOk = /[a-z]/.test(pw);
            const numOk = /[0-9]/.test(pw);
            const specialOk = /[^A-Za-z0-9]/.test(pw);

            if (lengthOk) score++;
            if (upperOk) score++;
            if (lowerOk) score++;
            if (numOk) score++;
            if (specialOk) score++;

            // ⭐ 게이지 길이
            bar.style.width = (score * 20) + "%";

            // ⭐ 색상 + 메시지
            if (score <= 2) {
                errorEl.textContent = "보안등급: 약함 (위험)";
                errorEl.style.color = "#ff4d4d";
                bar.style.backgroundColor = "#ff4d4d";
            } else if (score === 3) {
                errorEl.textContent = "보안등급: 보통 (조금 더 강화하세요)";
                errorEl.style.color = "#ffa500";
                bar.style.backgroundColor = "#ffa500";
            } else if (score === 4) {
                errorEl.textContent = "보안등급: 강함 (안전한 편)";
                errorEl.style.color = "#00c853";
                bar.style.backgroundColor = "#00c853";
            } else if (score === 5) {
                errorEl.textContent = "보안등급: 매우 강함 (아주 안전)";
                errorEl.style.color = "#00ff9d";
                bar.style.backgroundColor = "#00ff9d";
            }

            if (!lengthOk || !upperOk || !lowerOk || !numOk || !specialOk) {
                errorEl.textContent += " / 10자 이상, 대소문자·숫자·특수문자 포함";
            }
        }

        function checkPasswordMatch() {
            const pw1 = password1.value;
            const pw2 = password2.value;

            if (!pw2) {
                matchMsg.textContent = "";
                return;
            }

            if (pw1 === pw2) {
                matchMsg.textContent = "비밀번호가 일치합니다.";
                matchMsg.style.color = "#00ff9d";
            } else {
                matchMsg.textContent = "비밀번호가 서로 다릅니다.";
                matchMsg.style.color = "#ff4d4d";
            }
        }

        password1.addEventListener("input", () => {
            checkPasswordStrength();
            checkPasswordMatch();
        });

        password2.addEventListener("input", checkPasswordMatch);
    }

    // ===== 로그인 비밀번호 보기 =====
    const pwInput = document.getElementById("login-password");
    const toggleBtn = document.getElementById("togglePw");

    if (pwInput && toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            pwInput.type = pwInput.type === "password" ? "text" : "password";
        });
    }

});

const bar = document.getElementById("pw-strength-bar");

function checkPasswordStrength() {
    const pw = password1.value;

    if (!pw) {
        errorEl.textContent = "";
        bar.style.width = "0%";
        return;
    }

    let score = 0;

    const lengthOk = pw.length >= 10;
    const upperOk = /[A-Z]/.test(pw);
    const lowerOk = /[a-z]/.test(pw);
    const numOk = /[0-9]/.test(pw);
    const specialOk = /[^A-Za-z0-9]/.test(pw);

    if (lengthOk) score++;
    if (upperOk) score++;
    if (lowerOk) score++;
    if (numOk) score++;
    if (specialOk) score++;

    // 🔹 게이지 길이 (0~100%)
    bar.style.width = (score * 20) + "%";

    // 🔹 등급별 UI
    if (score <= 2) {
        errorEl.textContent = "보안등급: 약함";
        errorEl.style.color = "#ff4d4d";
        bar.style.backgroundColor = "#ff4d4d";
    } else if (score === 3) {
        errorEl.textContent = "보안등급: 보통";
        errorEl.style.color = "#ffa500";
        bar.style.backgroundColor = "#ffa500";
    } else if (score === 4) {
        errorEl.textContent = "보안등급: 강함";
        errorEl.style.color = "#00c853";
        bar.style.backgroundColor = "#00c853";
    } else if (score === 5) {
        errorEl.textContent = "보안등급: 매우 강함";
        errorEl.style.color = "#00ff9d";
        bar.style.backgroundColor = "#00ff9d";
    }

    // 🔹 조건 부족 시 안내 추가
    if (!lengthOk || !upperOk || !lowerOk || !numOk || !specialOk) {
        errorEl.textContent += " / 10자 이상, 대소문자·숫자·특수문자 포함";
    }
}