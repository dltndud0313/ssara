<template>
  <div class="screen-view">
    <header class="header">
      <button class="back-btn" @click="$router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
      <h1 class="header-title">로봇 화면</h1>
      <div class="header-spacer"></div>
    </header>

    <main class="content">
      <!-- 실시간 화면 영역 -->
      <section class="video-section">
        <div class="video-container">
          <div v-if="!isStreaming" class="video-placeholder">
            <div class="placeholder-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                <line x1="8" y1="21" x2="16" y2="21"/>
                <line x1="12" y1="17" x2="12" y2="21"/>
              </svg>
            </div>
            <p class="placeholder-text">로봇 화면을 불러오는 중...</p>
            <p class="placeholder-sub">로봇이 연결되면 실시간 화면이 표시됩니다</p>
          </div>
          <div v-else class="video-stream">
            <img :src="streamUrl" alt="로봇 카메라 화면" class="stream-image" />
          </div>
        </div>

        <!-- 연결 상태 -->
        <div class="connection-info">
          <div class="status-badge" :class="{ online: isOnline }">
            <span class="dot"></span>
            {{ isOnline ? '실시간 연결됨' : '연결 대기 중' }}
          </div>
          <span class="last-update" v-if="lastUpdate">{{ lastUpdate }}</span>
        </div>
      </section>

      <!-- 화면 컨트롤 -->
      <section class="control-section">
        <h3 class="section-title">화면 제어</h3>
        <div class="control-buttons">
          <button class="control-btn" @click="refreshStream" :disabled="!isOnline">
            <div class="control-icon refresh">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="23 4 23 10 17 10"/>
                <polyline points="1 20 1 14 7 14"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
              </svg>
            </div>
            <span>새로고침</span>
          </button>
          <button class="control-btn" @click="toggleFullscreen">
            <div class="control-icon fullscreen">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="15 3 21 3 21 9"/>
                <polyline points="9 21 3 21 3 15"/>
                <line x1="21" y1="3" x2="14" y2="10"/>
                <line x1="3" y1="21" x2="10" y2="14"/>
              </svg>
            </div>
            <span>전체화면</span>
          </button>
          <button class="control-btn" @click="captureScreen" :disabled="!isStreaming">
            <div class="control-icon capture">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                <circle cx="12" cy="13" r="4"/>
              </svg>
            </div>
            <span>캡처</span>
          </button>
        </div>
      </section>

      <!-- 로봇 상태 정보 -->
      <section class="status-section">
        <h3 class="section-title">로봇 상태</h3>
        <div class="status-cards">
          <div class="status-card">
            <div class="status-icon battery" :class="batteryClass">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="1" y="6" width="18" height="12" rx="2" ry="2"/>
                <line x1="23" y1="13" x2="23" y2="11"/>
              </svg>
            </div>
            <div class="status-content">
              <span class="status-value">{{ currentBattery }}%</span>
              <span class="status-label">배터리</span>
            </div>
          </div>
          <div class="status-card">
            <div class="status-icon state">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <div class="status-content">
              <span class="status-value">{{ robotState }}</span>
              <span class="status-label">활동 상태</span>
            </div>
          </div>
        </div>
      </section>

      <div class="bottom-spacer"></div>
    </main>

    <!-- 하단 네비게이션 -->
    <nav class="bottom-nav">
      <button class="nav-item active" @click="$router.push('/home')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span>홈</span>
      </button>
      <button class="nav-item" @click="$router.push('/location')">
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
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRobotStore } from '@/stores/robotStore';

const robotStore = useRobotStore();

const isStreaming = ref(false);
const streamUrl = ref('');
const lastUpdate = ref('');

// WebSocket 연결 관리
onMounted(() => {
  robotStore.connectWebSocket();
  // 실제 스트리밍 연결 시도 (예시)
  startStream();
});

onUnmounted(() => {
  robotStore.disconnectWebSocket();
  stopStream();
});

// 로봇 상태
const isOnline = computed(() => robotStore.robotStatus.isOnline);
const currentBattery = computed(() => robotStore.robotStatus.battery || 0);
const robotState = computed(() => robotStore.robotStatus.state || '대기');

const batteryClass = computed(() => {
  if (currentBattery.value <= 20) return 'low';
  if (currentBattery.value <= 50) return 'medium';
  return 'high';
});

// 로봇 카메라 MJPEG 스트림 URL
const ROBOT_STREAM_URL = 'http://192.168.100.246:8080/stream?topic=/camera/color/image_raw&type=mjpeg&width=560&height=315';

// 스트림 시작
const startStream = () => {
  streamUrl.value = ROBOT_STREAM_URL;
  isStreaming.value = true;
  updateLastTime();
};

// 스트림 중지
const stopStream = () => {
  isStreaming.value = false;
  streamUrl.value = '';
};

// 새로고침
const refreshStream = () => {
  stopStream();
  setTimeout(() => {
    startStream();
  }, 500);
};

// 전체화면
const toggleFullscreen = () => {
  const videoContainer = document.querySelector('.video-container');
  if (videoContainer) {
    if (!document.fullscreenElement) {
      videoContainer.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
  }
};

// 화면 캡처
const captureScreen = () => {
  alert('화면 캡처 기능은 준비 중입니다.');
};

// 마지막 업데이트 시간
const updateLastTime = () => {
  const now = new Date();
  lastUpdate.value = now.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
};
</script>

<style scoped>
.screen-view {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 80px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-primary);
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-spacer {
  width: 40px;
}

.content {
  padding: 0 20px;
}

/* 비디오 섹션 */
.video-section {
  margin-top: 16px;
}

.video-container {
  background: #000;
  border-radius: 16px;
  overflow: hidden;
  aspect-ratio: 16/9;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 24px;
  text-align: center;
}

.placeholder-icon {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--gray-400);
}

.placeholder-text {
  font-size: 15px;
  font-weight: 500;
  color: var(--gray-300);
}

.placeholder-sub {
  font-size: 13px;
  color: var(--gray-500);
}

.video-stream {
  width: 100%;
  height: 100%;
}

.stream-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.connection-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
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

.last-update {
  font-size: 13px;
  color: var(--text-tertiary);
}

/* 컨트롤 섹션 */
.control-section {
  margin-top: 28px;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 14px;
}

.control-buttons {
  display: flex;
  gap: 12px;
}

.control-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 12px;
  background: var(--bg-primary);
  border-radius: 16px;
  transition: all 0.2s;
}

.control-btn:active:not(:disabled) {
  transform: scale(0.97);
  background: var(--gray-50);
}

.control-btn:disabled {
  opacity: 0.5;
}

.control-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-icon.refresh {
  background: var(--primary-light);
  color: var(--primary);
}

.control-icon.fullscreen {
  background: var(--success-light);
  color: var(--success);
}

.control-icon.capture {
  background: var(--warning-light);
  color: var(--warning);
}

.control-btn span {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

/* 상태 섹션 */
.status-section {
  margin-top: 28px;
}

.status-cards {
  display: flex;
  gap: 12px;
}

.status-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 16px;
}

.status-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-icon.battery.high {
  background: var(--success-light);
  color: var(--success);
}

.status-icon.battery.medium {
  background: var(--warning-light);
  color: var(--warning);
}

.status-icon.battery.low {
  background: #FEE2E2;
  color: #EF4444;
}

.status-icon.state {
  background: var(--primary-light);
  color: var(--primary);
}

.status-content {
  display: flex;
  flex-direction: column;
}

.status-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.status-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
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
  padding: 0 8px;
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  flex: 1 1 0%;
  width: 100%;
  min-width: 0;
  padding: 8px 0;
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
