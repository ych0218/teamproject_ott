document.addEventListener("DOMContentLoaded", function () {

    // ===== 생년월일 =====
    const yearSelect = document.querySelector("[name='birth_year']");
    const monthSelect = document.querySelector("[name='birth_month']");
    const daySelect = document.querySelector("[name='birth_day']");

    const currentYear = new Date().getFullYear();

    // 초기 상태
    yearSelect.innerHTML = '<option value="">년도</option>';
    monthSelect.innerHTML = '<option value="">월</option>';
    daySelect.innerHTML = '<option value="">일</option>';

    monthSelect.disabled = true;
    daySelect.disabled = true;

    // 년도 생성
    for (let y = currentYear; y >= currentYear - 100; y--) {
        yearSelect.add(new Option(y + "년", y));
    }

    // 년도 선택 → 월 활성화
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

    // 월 선택 → 일 활성화
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

    // ===== 성별 버튼 =====
    const buttons = document.querySelectorAll(".gender-btn");

    buttons.forEach(btn => {
        btn.addEventListener("click", function () {

            // 스타일 초기화
            buttons.forEach(b => b.classList.remove("active"));

            // 클릭한 버튼 활성화
            this.classList.add("active");

            // radio 체크
            const radio = this.closest("label").querySelector("input");
            if (radio) {
                radio.checked = true;
            }
        });
    });

    // ===== 비밀번호 확인 =====
    const password1 = document.querySelector("[name='password1']");
    const password2 = document.querySelector("[name='password2']");
    const msg = document.getElementById("password-match-msg");

    function checkPasswordMatch() {
        const pw1 = password1.value;
        const pw2 = password2.value;

        if (!pw2) {
            msg.textContent = "";
            return;
        }

        if (pw1 === pw2) {
            msg.textContent = "비밀번호가 일치합니다.";
            msg.style.color = "#00ff9d";
        } else {
            msg.textContent = "비밀번호가 일치하지 않습니다.";
            msg.style.color = "#ff4d4d";
        }
    }

    password1.addEventListener("input", checkPasswordMatch);
    password2.addEventListener("input", checkPasswordMatch);

});