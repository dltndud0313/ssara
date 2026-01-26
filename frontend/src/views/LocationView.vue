<template>
  <div class="location">
    <header class="header">
      <h1 class="header-title">위치</h1>
      <div class="status-badge" :class="{ online: robotState.status === 'ONLINE' }">
        <span class="dot"></span>
        {{ robotState.status === 'ONLINE' ? '실시간' : '오프라인' }}
      </div>
    </header>

    <main class="content">
      <!-- 지도 영역 -->
      <section class="map-section">
        <div class="map-placeholder">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--gray-400)" stroke-width="1.5">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
          <p class="placeholder-text">지도를 불러오는 중</p>
          <p class="placeholder-sub">카카오맵 API 연동 예정</p>
        </div>

        <div class="location-card">
          <div class="location-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
          </div>
          <div class="location-info">
            <span class="location-label">현재 위치</span>
            <span class="location-address">{{ robotState.location }}</span>
          </div>
        </div>
      </section>

      <!-- 상태 카드 -->
      <section class="status-section">
        <div class="status-card">
          <div class="status-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="1" y="6" width="18" height="12" rx="2" ry="2"/>
              <line x1="23" y1="13" x2="23" y2="11"/>
            </svg>
          </div>
          <div class="status-content">
            <span class="status-value">{{ robotState.battery }}%</span>
            <span class="status-label">배터리</span>
          </div>
          <div class="battery-bar">
            <div class="battery-fill" :style="{ width: robotState.battery + '%' }"></div>
          </div>
        </div>

        <div class="status-card">
          <div class="status-icon orange">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
          </div>
          <div class="status-content">
            <span class="status-value">{{ activityStatus }}</span>
            <span class="status-label">활동 상태</span>
          </div>
        </div>
      </section>

      <!-- 오늘 이동 경로 -->
      <section class="route-section">
        <div class="section-header">
          <h3 class="section-title">오늘 이동 경로</h3>
          <span class="total-distance">{{ totalDistance }}km</span>
        </div>

        <div class="route-list">
          <div
            v-for="(route, index) in routes"
            :key="index"
            class="route-item"
            :class="{ current: index === 0 }"
          >
            <div class="route-marker">
              <div class="marker-dot"></div>
              <div v-if="index < routes.length - 1" class="marker-line"></div>
            </div>
            <div class="route-content">
              <span class="route-place">{{ route.place }}</span>
              <span class="route-time">{{ route.time }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 빠른 명령 -->
      <section class="command-section">
        <h3 class="section-title">빠른 명령</h3>
        <div class="command-list">
          <button class="command-btn" @click="sendCommand('home')">
            <div class="command-icon home">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
            </div>
            <span class="command-text">집으로 복귀</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </button>
          <button class="command-btn" @click="sendCommand('stay')">
            <div class="command-icon stay">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="6" y="4" width="4" height="16"/>
                <rect x="14" y="4" width="4" height="16"/>
              </svg>
            </div>
            <span class="command-text">제자리 대기</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </button>
        </div>
      </section>

      <div class="bottom-spacer"></div>
    </main>

    <!-- 하단 네비게이션 -->
    <nav class="bottom-nav">
      <button class="nav-item" @click="$router.push('/home')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span>홈</span>
      </button>
      <button class="nav-item active">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
          <circle cx="12" cy="10" r="3"/>
        </svg>
        <span>위치</span>
      </button>
      <button class="nav-item" @click="$router.push('/history')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        <span>기록</span>
      </button>
      <button class="nav-item" @click="$router.push('/profile')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        <span>내 정보</span>
      </button>
    </nav>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { robotState } from '../store.js';

const routes = ref([]);
const totalDistance = ref(0);
const activityStatus = ref('-');

const sendCommand = (cmd) => {
  const msgs = {
    home: '집으로 복귀 명령을 보냈어요',
    stay: '제자리 대기 명령을 보냈어요'
  };
  robotState.addLog(msgs[cmd], 'action');
  alert(msgs[cmd]);
};
</script>

<style scoped>
.location {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 80px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: var(--bg-primary);
}

.header-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--bg-tertiary);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-tertiary);
}

.status-badge.online {
  background: var(--success-light);
  color: var(--success);
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.content {
  padding: 0 20px 20px;
}

/* 지도 */
.map-section {
  margin: 0 -20px;
  position: relative;
}

.map-placeholder {
  height: 240px;
  background: linear-gradient(180deg, var(--gray-100) 0%, var(--gray-50) 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.placeholder-text {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-secondary);
}

.placeholder-sub {
  font-size: 13px;
  color: var(--text-tertiary);
}

.location-card {
  position: absolute;
  bottom: 16px;
  left: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--bg-primary);
  border-radius: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.location-icon {
  width: 36px;
  height: 36px;
  background: var(--primary-light);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
}

.location-info {
  display: flex;
  flex-direction: column;
}

.location-label {
  font-size: 12px;
  color: var(--success);
  font-weight: 600;
}

.location-address {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 상태 카드 */
.status-section {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.status-card {
  flex: 1;
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 16px;
}

.status-icon {
  width: 40px;
  height: 40px;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}

.status-icon.orange {
  background: var(--warning-light);
  color: var(--warning);
}

.status-content {
  display: flex;
  flex-direction: column;
}

.status-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.status-label {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

.battery-bar {
  height: 4px;
  background: var(--gray-200);
  border-radius: 2px;
  margin-top: 12px;
  overflow: hidden;
}

.battery-fill {
  height: 100%;
  background: var(--success);
  border-radius: 2px;
}

/* 이동 경로 */
.route-section {
  margin-top: 28px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
}

.total-distance {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary);
}

.route-list {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 8px 0;
}

.route-item {
  display: flex;
  padding: 12px 18px;
}

.route-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 14px;
}

.marker-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--gray-300);
  flex-shrink: 0;
}

.route-item.current .marker-dot {
  background: var(--primary);
  box-shadow: 0 0 0 4px var(--primary-light);
}

.marker-line {
  width: 2px;
  flex: 1;
  background: var(--gray-200);
  margin-top: 6px;
  min-height: 24px;
}

.route-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding-top: 0;
}

.route-place {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.route-time {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

/* 빠른 명령 */
.command-section {
  margin-top: 28px;
}

.command-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.command-btn {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  background: var(--bg-primary);
  border-radius: 14px;
  transition: background 0.2s;
}

.command-btn:active {
  background: var(--gray-50);
}

.command-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.command-icon.home {
  background: var(--primary-light);
  color: var(--primary);
}

.command-icon.stay {
  background: var(--warning-light);
  color: var(--warning);
}

.command-text {
  flex: 1;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  text-align: left;
}

.command-btn svg {
  color: var(--gray-400);
}

.bottom-spacer {
  height: 20px;
}

/* 하단 네비게이션 */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  max-width: 600px;
  margin: 0 auto;
  height: 72px;
  background: var(--bg-primary);
  border-top: 1px solid var(--gray-100);
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  color: var(--gray-400);
}

.nav-item svg {
  width: 24px;
  height: 24px;
}

.nav-item span {
  font-size: 11px;
  font-weight: 500;
}

.nav-item.active {
  color: var(--primary);
}
</style>
