<template>
  <div class="signup-container">
    <div class="header-section">
      <h1 class="app-title">회원가입</h1>
      <p class="app-subtitle">반려견과 함께하는 스마트한 라이프</p>
    </div>

    <form @submit.prevent="handleSignup" class="form-section">
      
      <div class="input-group">
        <label>이름</label>
        <div class="input-wrapper">
          <input type="text" v-model="name" placeholder="홍길동" required />
        </div>
      </div>

      <div class="input-group">
        <label>이메일</label>
        <div class="input-wrapper">
          <input type="email" v-model="email" placeholder="example@email.com" required />
        </div>
      </div>

      <div class="input-group">
        <label>비밀번호</label>
        <div class="input-wrapper">
          <input type="password" v-model="password" placeholder="비밀번호 입력" required />
        </div>
      </div>

      <div class="input-group">
        <label>전화번호</label>
        <div class="input-wrapper">
          <input type="tel" v-model="phoneNumber" placeholder="010-0000-0000" />
        </div>
      </div>

      <div class="input-group highlight">
        <label>로봇 시리얼 번호</label>
        <div class="input-wrapper">
          <input type="text" v-model="serialNo" placeholder="GAE-001" required />
        </div>
        <p class="helper-text">* 로봇 몸체에 적힌 번호를 입력하세요.</p>
      </div>

      <button type="submit" class="signup-btn">가입하기</button>
    </form>

    <div class="footer-section">
      <p>이미 계정이 있으신가요? <span class="login-link" @click="$router.push('/')">로그인</span></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

const name = ref('');
const email = ref('');
const password = ref('');
const phoneNumber = ref('');
const serialNo = ref(''); // 로봇 시리얼 번호

const handleSignup = async () => {
  try {
    // 백엔드 회원가입 API 호출
    const response = await axios.post('/api/auth/signup', {
      name: name.value,
      email: email.value,
      password: password.value,
      phoneNumber: phoneNumber.value,
      serialNo: serialNo.value
    });

    alert("회원가입이 완료되었습니다! 로그인해주세요.");
    router.push('/'); // 로그인 화면으로 이동

  } catch (error) {
    console.error("회원가입 실패:", error);
    if (error.response && error.response.data) {
      // 백엔드에서 보낸 에러 메시지 (예: 이미 등록된 로봇입니다)
      alert(error.response.data); 
    } else {
      alert("회원가입 중 오류가 발생했습니다.");
    }
  }
};
</script>

<style scoped>
/* 보라색 테마 재사용 */
.signup-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 40px 24px;
  background-color: #ffffff;
  font-family: 'Pretendard', sans-serif;
}
.header-section { margin-top: 20px; margin-bottom: 30px; text-align: center; }
.app-title { font-size: 24px; font-weight: 800; color: #333; margin: 0 0 8px 0; }
.app-subtitle { font-size: 14px; color: #888; margin: 0; }
.form-section { flex: 1; }
.input-group { margin-bottom: 16px; }
.input-group label { display: block; font-size: 13px; color: #666; font-weight: 600; margin-bottom: 6px; }
.input-wrapper input {
  width: 100%; height: 50px; padding: 0 16px; border: 1px solid #E5E5E5; border-radius: 12px;
  background-color: #FAFAFA; font-size: 15px; box-sizing: border-box;
}
.input-wrapper input:focus { border-color: #6A67CE; background-color: #fff; outline: none; }

/* 시리얼 번호 강조 */
.highlight label { color: #6A67CE; }
.highlight input { border-color: #D6D5F5; background-color: #F8F7FF; }
.helper-text { font-size: 11px; color: #888; margin-top: 4px; margin-left: 4px; }

.signup-btn {
  width: 100%; height: 56px; background-color: #6A67CE; color: white; font-size: 16px; font-weight: 700;
  border: none; border-radius: 14px; margin-top: 20px; cursor: pointer;
}
.footer-section { text-align: center; margin-top: 30px; font-size: 14px; color: #888; }
.login-link { color: #6A67CE; font-weight: 700; margin-left: 5px; cursor: pointer; }
</style>