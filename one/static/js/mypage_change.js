document.addEventListener('DOMContentLoaded', function() {
    console.log("마이페이지 수정 JS 로드 완료");

    const currentPw = document.getElementById('current_pw');
    const newPw = document.getElementById('new_pw');
    const confirmPw = document.getElementById('confirm_pw');
    const saveBtn = document.getElementById('save_btn');
    const pw1 = document.getElementById('pw1') || document.getElementById('new_pw');
    const pw2 = document.getElementById('pw2') || document.getElementById('confirm_pw');
    const pwMsg = document.getElementById('pw_msg');
    const matchMsg = document.getElementById('match_msg');

    // 버튼에 심어둔 유저 이메일 가져오기
    const userEmail = saveBtn.dataset.email;

    function validate() {
    const currVal = currentPw.value.trim();
    const newVal = newPw.value.trim();
    const cfmVal = confirmPw.value.trim();

    // 💡 HTML의 signup_method 정보를 가져옵니다 (데이터 속성 등 활용)
    const isSocial = "{{ user.signup_method }}" !== 'email'; // 실제 구현에 맞춰 변수 전달 필요

    // 1. 소셜 유저면 현재비번 무시(true), 일반 유저면 4자 이상 입력 확인
    const isCurrentOk = isSocial ? true : currVal.length >= 4;

    let isNewOk = true;

        // 최종 버튼 활성화 여부
       saveBtn.disabled = !(isCurrentOk && isNewOk);
}


    [currentPw, newPw, confirmPw].forEach(el => {
        if(el) el.addEventListener('input', validate);
    });
});