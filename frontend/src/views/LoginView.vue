<template>
  <div class="login-container">
    <div class="header-section">
      <div class="logo-box">
        <span class="logo-emoji">🐶</span> 
      </div>
      <h1 class="app-title">GAE-CLIENT</h1>
      <p class="app-subtitle">AIoT 로봇 반려견 관리 플랫폼</p>
    </div>

    <form @submit.prevent="handleLogin" class="form-section">
      
      <div class="input-group">
        <label for="email">이메일</label>
        <div class="input-wrapper">
          <input 
            id="email" 
            type="email" 
            v-model="email" 
            placeholder="example@email.com" 
            required 
          />
        </div>
      </div>

      <div class="input-group">
        <label for="password">비밀번호</label>
        <div class="input-wrapper">
          <input 
            id="password" 
            :type="showPassword ? 'text' : 'password'" 
            v-model="password" 
            placeholder="비밀번호를 입력하세요" 
            required 
          />
          <span class="eye-icon" @click="togglePassword">
            <svg v-if="showPassword" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
          </span>
        </div>
      </div>

      <div class="options-row">
        <label class="checkbox-label">
          <input type="checkbox" v-model="rememberMe" />
          <span class="custom-check"></span>
          로그인 상태 유지
        </label>
        <span class="forgot-pw">비밀번호 찾기</span>
      </div>

      <button type="submit" class="login-btn">로그인</button>
    </form>

   <div class="footer-section">
  <p>아직 계정이 없으신가요? <span class="signup-link" @click="router.push('/signup')">회원가입</span></p>
</div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

const email = ref('');
const password = ref('');
const rememberMe = ref(false);
const showPassword = ref(false);

const togglePassword = () => {
  showPassword.value = !showPassword.value;
};

const handleLogin = async () => {
  if (!email.value || !password.value) {
    alert('이메일과 비밀번호를 입력해주세요.');
    return;
  }

  try {
    // 1. 백엔드 로그인 API 호출 (/api는 vite.config.js에서 프록시됨)
    const response = await axios.post('/api/auth/login', {
      email: email.value,
      password: password.value
    });

    console.log("로그인 성공!", response.data);

    // 2. 토큰 저장
    const { accessToken } = response.data;
    localStorage.setItem('accessToken', accessToken);

    // 3. 메인 화면 이동
    router.push('/home');

  } catch (error) {
    console.error("로그인 실패:", error);
    if (error.response && error.response.status === 401) {
      alert("아이디 또는 비밀번호가 잘못되었습니다.");
    } else {
      alert("로그인 서버 연결 실패");
    }
  }
};
</script>

<style scoped>
/* (이전과 동일한 보라색 테마 스타일 유지) */
.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 40px 24px;
  justify-content: space-between;
  background-color: var(--bg-color);
}
.header-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 60px;
  margin-bottom: 40px;
}
.logo-box {
  width: 80px;
  height: 80px;
  background-color: var(--primary-color);
  border-radius: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
  box-shadow: 0 10px 20px rgba(106, 103, 206, 0.2);
}
.logo-emoji { font-size: 40px; }
.app-title {
  font-size: 24px; font-weight: 800; color: var(--text-main); margin: 0 0 8px 0;
}
.app-subtitle { font-size: 14px; color: var(--text-sub); margin: 0; }
.form-section { width: 100%; flex: 1; }
.input-group { margin-bottom: 20px; }
.input-group label {
  display: block; font-size: 13px; color: #666; font-weight: 600; margin-bottom: 8px; margin-left: 4px;
}
.input-wrapper { position: relative; width: 100%; }
.input-wrapper input {
  width: 100%; height: 52px; padding: 0 16px; padding-right: 40px;
  border: 1px solid var(--border-color); border-radius: 12px;
  background-color: var(--input-bg); font-size: 15px; color: var(--text-main); transition: all 0.2s;
}
.input-wrapper input:focus { border-color: var(--primary-color); background-color: #fff; }
.eye-icon {
  position: absolute; right: 16px; top: 50%; transform: translateY(-50%); cursor: pointer; display: flex; align-items: center;
}
.options-row {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; font-size: 13px;
}
.checkbox-label { display: flex; align-items: center; cursor: pointer; color: #666; }
.checkbox-label input { display: none; }
.custom-check {
  width: 18px; height: 18px; border: 1px solid #ddd; border-radius: 4px; margin-right: 8px; display: inline-block; position: relative;
}
.checkbox-label input:checked + .custom-check { background-color: var(--primary-color); border-color: var(--primary-color); }
.checkbox-label input:checked + .custom-check::after {
  content: '✔'; color: white; font-size: 12px; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
}
.forgot-pw { color: var(--primary-color); font-weight: 600; cursor: pointer; }
.login-btn {
  width: 100%; height: 56px; background-color: var(--primary-color); color: white; font-size: 16px; font-weight: 700; border-radius: 14px; box-shadow: 0 8px 20px rgba(106, 103, 206, 0.3); transition: transform 0.1s;
}
.login-btn:active { transform: scale(0.98); }
.footer-section { text-align: center; margin-top: 20px; font-size: 14px; color: var(--text-sub); }
.signup-link { color: var(--primary-color); font-weight: 700; margin-left: 5px; cursor: pointer; }
</style>