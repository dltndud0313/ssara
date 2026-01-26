// src/api/index.js
import axios from 'axios';

// Axios 인스턴스 생성 (인증 토큰 자동 첨부)
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// 요청 인터셉터: 토큰 자동 첨부
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 응답 인터셉터: 401 에러 시 로그인 페이지로 이동
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('accessToken');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export default api;

// API 함수들
export const memberApi = {
  // 내 정보 조회
  getMyInfo: () => api.get('/members/me'),

  // 내 정보 수정
  updateMyInfo: (data) => api.patch('/members/me', data),

  // 회원 탈퇴
  deleteAccount: () => api.delete('/members/me')
};

export const authApi = {
  // 로그인
  login: (data) => axios.post('/api/auth/login', data),

  // 회원가입
  signup: (data) => axios.post('/api/auth/signup', data)
};
