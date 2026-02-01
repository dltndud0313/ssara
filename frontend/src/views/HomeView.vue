<template>
  <div class="home">
    <!-- 헤더 -->
    <header class="header">
      <div class="header-left">
        <span class="greeting">안녕하세요</span>
        <h1 class="title">우리 가족 돌봄</h1>
      </div>
      <button class="icon-btn logout-btn" @click="handleLogout" title="로그아웃">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
      </button>
    </header>

    <!-- 메인 콘텐츠 -->
    <main class="content">
      <!-- 로봇 상태 카드 -->
      <section class="status-card" :class="{ offline: !isOnline }">
        <div class="status-header">
          <div class="robot-avatar">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/>
              <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
              <line x1="9" y1="9" x2="9.01" y2="9"/>
              <line x1="15" y1="9" x2="15.01" y2="9"/>
            </svg>
          </div>
          <div class="robot-info">
            <h2 class="robot-name">{{ robotState.name }}</h2>
            <div class="connection-status">
              <span class="status-dot" :class="{ online: isOnline }"></span>
              <span class="status-text">{{ isOnline ? '연결됨' : '연결 안 됨' }}</span>
            </div>
          </div>
        </div>

        <div class="status-body">
          <div class="battery-section">
            <div class="battery-header">
              <div class="battery-icon" :class="batteryClass">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="1" y="6" width="18" height="12" rx="2" ry="2"/>
                  <line x1="23" y1="13" x2="23" y2="11"/>
                </svg>
              </div>
              <span class="battery-percent" :class="batteryClass">{{ currentBattery }}%</span>
              <span class="battery-status">{{ batteryStatusText }}</span>
            </div>
            <div class="battery-bar">
              <div class="battery-fill" :class="batteryClass" :style="{ width: currentBattery + '%' }"></div>
            </div>
          </div>
          <div class="status-item">
            <span class="label">현재 위치</span>
            <span class="value location">{{ currentLocation }}</span>
          </div>
        </div>

        <button class="location-btn" @click="$router.push('/location')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
          위치 확인하기
        </button>
      </section>

      <!-- 오늘의 요약 -->
      <section class="summary-section">
        <h3 class="section-title">오늘 하루</h3>
        <div class="summary-cards">
          <div class="summary-card">
            <div class="summary-icon walk">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <div class="summary-content">
              <span class="summary-value">{{ todaySummary.walkTime }}분</span>
              <span class="summary-label">산책 시간</span>
            </div>
          </div>
          <div class="summary-card">
            <div class="summary-icon safe">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
            </div>
            <div class="summary-content">
              <span class="summary-value">{{ todaySummary.alerts }}건</span>
              <span class="summary-label">이상 감지</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 최근 활동 -->
      <section class="activity-section">
        <div class="section-header">
          <h3 class="section-title">최근 활동</h3>
          <button class="more-btn" @click="$router.push('/history')">더보기</button>
        </div>

        <div class="activity-list">
          <div
            v-for="(log, index) in displayLogs"
            :key="index"
            class="activity-item"
          >
            <div class="activity-icon" :class="log.type">
              <svg v-if="log.type === 'info'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="16" x2="12" y2="12"/>
                <line x1="12" y1="8" x2="12.01" y2="8"/>
              </svg>
              <svg v-else-if="log.type === 'warning'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </div>
            <div class="activity-content">
              <span class="activity-msg">{{ log.msg }}</span>
              <span class="activity-time">{{ log.time }}</span>
            </div>
          </div>
        </div>
      </section>

      <div class="bottom-spacer"></div>
    </main>

    <!-- 하단 네비게이션 -->
    <nav class="bottom-nav">
      <button class="nav-item active">
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
import { useRouter } from 'vue-router';
import { robotState } from '../store.js';
import { useAuthStore } from '../stores/authStore';
import { useRobotStore } from '@/stores/robotStore';
import { activityApi } from '@/api';

const router = useRouter();
const authStore = useAuthStore();
const robotStore = useRobotStore();

// API에서 가져온 초기 데이터
const apiSummary = ref({ walkTime: 0, alerts: 0 });
const apiLogs = ref([]);

// 실시간 일일 요약 (API 데이터 + WebSocket 실시간 데이터)
const todaySummary = computed(() => ({
  walkTime: robotStore.dailySummary.walkTime || apiSummary.value.walkTime || 0,
  alerts: robotStore.dailySummary.alerts || apiSummary.value.alerts || 0
}));

const loading = ref(true);

onMounted(async () => {
  await robotState.fetchRobot();
  // 오늘 요약 정보 API에서 가져오기
  try {
    const summaryRes = await activityApi.getTodaySummary();
    apiSummary.value = {
      walkTime: summaryRes.data.walkTime || 0,
      alerts: summaryRes.data.alerts || 0
    };
  } catch (e) {
    console.error('요약 정보 로드 실패:', e);
  }
  // 오늘 활동 로그 API에서 가져오기
  try {
    const logsRes = await activityApi.getTodayLogs();
    apiLogs.value = logsRes.data.slice(0, 4);
  } catch (e) {
    console.error('활동 로그 로드 실패:', e);
  }
  // WebSocket 연결 (실시간 데이터)
  robotStore.connectWebSocket();
  loading.value = false;
});

onUnmounted(() => {
  robotStore.disconnectWebSocket();
});

// 실시간 배터리 값 (WebSocket에서 받은 값 사용, 없으면 API 값 사용)
const currentBattery = computed(() => {
  return robotStore.robotStatus.battery || robotState.battery;
});

// 실시간 위치 값 (WebSocket에서 받은 값 사용)
const currentLocation = computed(() => {
  if (robotStore.robotPose.x || robotStore.robotPose.y) {
    return `(${robotStore.robotPose.x.toFixed(1)}, ${robotStore.robotPose.y.toFixed(1)})`;
  }
  return robotState.location || '위치 정보 없음';
});

// 실시간 연결 상태
const isOnline = computed(() => {
  return robotStore.robotStatus.isOnline || robotState.status === 'ONLINE';
});

const batteryClass = computed(() => {
  if (currentBattery.value <= 20) return 'low';
  if (currentBattery.value <= 50) return 'medium';
  return 'high';
});

const batteryStatusText = computed(() => {
  if (currentBattery.value <= 20) return '충전 필요';
  if (currentBattery.value <= 50) return '보통';
  return '충분';
});

// 최근 활동 로그 (WebSocket 실시간 + API에서 가져온 로그)
const displayLogs = computed(() => {
  const wsLogs = robotStore.activityLogs || [];
  const dbLogs = apiLogs.value || [];
  // WebSocket 실시간 로그 우선, 그 다음 DB 로그
  return [...wsLogs, ...dbLogs].slice(0, 4);
});

const handleLogout = () => {
  authStore.logout();
  router.push('/');
};
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 80px;
}

/* 헤더 */
.header {
  background: var(--bg-primary);
  padding: 16px 20px 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.greeting {
  font-size: 13px;
  color: var(--text-tertiary);
  display: block;
  margin-bottom: 2px;
}

.title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.icon-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: background 0.2s;
}

.icon-btn:active {
  background: var(--gray-200);
}

.logout-btn {
  color: var(--text-tertiary);
}

.logout-btn:hover {
  color: #EF4444;
}

/* 메인 콘텐츠 */
.content {
  padding: 0 20px;
  overflow-x: hidden;
}

/* 상태 카드 */
.status-card {
  background: var(--bg-primary);
  border-radius: 20px;
  padding: 20px;
  margin-top: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  max-width: 100%;
  overflow: hidden;
  box-sizing: border-box;
}

.status-card.offline {
  border: 1px solid var(--gray-200);
}

.status-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}

.robot-avatar {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, var(--primary) 0%, #5BA0F5 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.robot-info {
  min-width: 0;
  overflow: hidden;
}

.robot-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--gray-400);
}

.status-dot.online {
  background: var(--success);
}

.status-text {
  font-size: 13px;
  color: var(--text-tertiary);
}

.status-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 12px;
  margin-bottom: 16px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-item .label {
  font-size: 14px;
  color: var(--text-secondary);
}

.status-item .value.location {
  font-size: 13px;
  font-weight: 500;
  max-width: 180px;
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 배터리 섹션 */
.battery-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.battery-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.battery-icon {
  display: flex;
  align-items: center;
}

.battery-icon.high { color: var(--success); }
.battery-icon.medium { color: #F59E0B; }
.battery-icon.low { color: #EF4444; }

.battery-percent {
  font-size: 20px;
  font-weight: 700;
}

.battery-percent.high { color: var(--success); }
.battery-percent.medium { color: #F59E0B; }
.battery-percent.low { color: #EF4444; }

.battery-status {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-left: auto;
}

.battery-bar {
  width: 100%;
  height: 8px;
  background: var(--gray-200);
  border-radius: 4px;
  overflow: hidden;
}

.battery-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s, background 0.3s;
}

.battery-fill.high { background: var(--success); }
.battery-fill.medium { background: #F59E0B; }
.battery-fill.low { background: #EF4444; }

.location-btn {
  width: 100%;
  height: 48px;
  background: var(--primary);
  color: white;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: opacity 0.2s;
}

.location-btn:active {
  opacity: 0.9;
}

/* 섹션 공통 */
.section-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 14px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.more-btn {
  font-size: 14px;
  color: var(--text-tertiary);
}

/* 오늘의 요약 */
.summary-section {
  margin-top: 28px;
}

.summary-cards {
  display: flex;
  gap: 12px;
}

.summary-card {
  flex: 1;
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 18px;
  display: flex;
  align-items: center;
  gap: 14px;
}

.summary-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.summary-icon.walk {
  background: var(--primary-light);
  color: var(--primary);
}

.summary-icon.safe {
  background: var(--success-light);
  color: var(--success);
}

.summary-content {
  display: flex;
  flex-direction: column;
}

.summary-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.summary-label {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

/* 최근 활동 */
.activity-section {
  margin-top: 28px;
}

.activity-list {
  background: var(--bg-primary);
  border-radius: 16px;
  overflow: hidden;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  border-bottom: 1px solid var(--gray-100);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon.info {
  background: var(--primary-light);
  color: var(--primary);
}

.activity-icon.warning {
  background: var(--warning-light);
  color: var(--warning);
}

.activity-icon.action {
  background: var(--success-light);
  color: var(--success);
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-msg {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.activity-time {
  font-size: 12px;
  color: var(--text-tertiary);
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
  gap: 4px;
  padding: 8px 16px;
  color: var(--gray-400);
  transition: color 0.2s;
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
