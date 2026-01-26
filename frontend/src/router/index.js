// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import SignupView from '../views/SignupView.vue'
import ProfileView from '../views/ProfileView.vue'
import LocationView from '../views/LocationView.vue'
import HistoryView from '../views/HistoryView.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginView
  },
  {
    path: '/signup',
    name: 'Signup',
    component: SignupView
  },
  {
    path: '/home',
    name: 'Home',
    component: HomeView,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/location',
    name: 'Location',
    component: LocationView,
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: HistoryView,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 네비게이션 가드: 인증 필요한 페이지 보호
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('accessToken')

  if (to.meta.requiresAuth && !token) {
    // 인증 필요한 페이지인데 토큰 없으면 로그인으로
    next('/')
  } else if ((to.path === '/' || to.path === '/signup') && token) {
    // 로그인/회원가입 페이지인데 토큰 있으면 홈으로
    next('/home')
  } else {
    next()
  }
})

export default router
