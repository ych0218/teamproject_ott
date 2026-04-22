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
    const password1 =
        document.getElementById("password1") ||
        document.getElementById("new_pw");

    const password2 =
        document.getElementById("password2") ||
        document.getElementById("confirm_pw");

    const errorEl = document.getElementById("pw-error");

    const matchMsg =
        document.getElementById("password-match-msg") ||
        document.getElementById("match_msg");

    const bar = document.getElementById("pw-strength-bar");
    const pwBarWrap = document.querySelector(".pw-bar");

    const form = document.querySelector("form");

    if (password1) {

        // ===== 비밀번호 조건 검사 함수 (핵심) =====
        function validatePassword(pw) {
            return {
                lengthOk: pw.length >= 10,
                upperOk: /[A-Z]/.test(pw),
                lowerOk: /[a-z]/.test(pw),
                numOk: /[0-9]/.test(pw),
                specialOk: /[^A-Za-z0-9]/.test(pw)
            };
        }

        // ===== 비밀번호 강도 체크 =====
        function checkPasswordStrength() {
            const pw = password1.value;

            // 게이지 활성화
            if (pwBarWrap) {
                pw ? pwBarWrap.classList.add("active") : pwBarWrap.classList.remove("active");
            }

            if (!pw) {
                if (errorEl) errorEl.textContent = "";
                if (bar) bar.style.width = "0%";
                return;
            }

            const v = validatePassword(pw);

            let score = 0;
            if (v.lengthOk) score++;
            if (v.upperOk) score++;
            if (v.lowerOk) score++;
            if (v.numOk) score++;
            if (v.specialOk) score++;

            // ===== 게이지 =====
            if (bar) {
                bar.style.width = (score * 20) + "%";

                if (score <= 2) bar.style.backgroundColor = "#ff4d4d";
                else if (score === 3) bar.style.backgroundColor = "#ffa500";
                else if (score === 4) bar.style.backgroundColor = "#00c853";
                else if (score === 5) bar.style.backgroundColor = "#00ff9d";
            }

            // ===== 메시지 =====
            if (errorEl) {
                if (score <= 2) {
                    errorEl.textContent = "보안등급: 약함";
                    errorEl.style.color = "#ff4d4d";
                } else if (score === 3) {
                    errorEl.textContent = "보안등급: 보통";
                    errorEl.style.color = "#ffa500";
                } else if (score === 4) {
                    errorEl.textContent = "보안등급: 강함";
                    errorEl.style.color = "#00c853";
                } else if (score === 5) {
                    errorEl.textContent = "사용 가능한 안전한 비밀번호입니다.";
                    errorEl.style.color = "#00ff9d";
                }
            }
        }

        // ===== 비밀번호 일치 검사 =====
        function checkPasswordMatch() {
            if (!password2 || !matchMsg) return;

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

        // ===== 이벤트 =====
        password1.addEventListener("input", () => {
            checkPasswordStrength();
            checkPasswordMatch();
        });

        if (password2) {
            password2.addEventListener("input", checkPasswordMatch);
        }

        // ===== 제출 차단 (핵심🔥) =====
        if (form) {
            form.addEventListener("submit", function (e) {
                const pw = password1.value;
                const v = validatePassword(pw);

                // 비밀번호 불일치
                if (password2 && pw !== password2.value) {
                    e.preventDefault();
                    if (matchMsg) {
                        matchMsg.textContent = "비밀번호가 일치하지 않습니다.";
                        matchMsg.style.color = "#ff4d4d";
                    }
                    password2.focus();
                    return;
                }

                // 조건 미충족 → 가입 차단
                if (!v.lengthOk || !v.upperOk || !v.lowerOk || !v.numOk || !v.specialOk) {
                    e.preventDefault();

                    if (errorEl) {
                        errorEl.textContent = "모든 조건을 만족해야 가입 가능합니다.";
                        errorEl.style.color = "#ff4d4d";
                    }

                    password1.focus();
                }
            });
        }
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