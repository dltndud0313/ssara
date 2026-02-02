<template>
  <div class="healthcare-view">
    <header class="header">
      <button class="back-btn" @click="$router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
      <h1 class="header-title">헬스케어</h1>
      <div class="header-spacer"></div>
    </header>

    <main class="content">
      <!-- 오늘의 건강 요약 -->
      <section class="summary-section">
        <div class="summary-card">
          <div class="summary-header">
            <div class="summary-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
              </svg>
            </div>
            <div class="summary-title">
              <h2>오늘의 건강</h2>
              <span class="summary-date">{{ formattedDate }}</span>
            </div>
          </div>
          <div class="health-score">
            <div class="score-circle" :class="healthScoreClass">
              <span class="score-value">{{ healthScore }}</span>
              <span class="score-label">점</span>
            </div>
            <p class="score-message">{{ healthMessage }}</p>
          </div>
        </div>
      </section>

      <!-- 활동 지표 -->
      <section class="metrics-section">
        <h3 class="section-title">활동 지표</h3>
        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-icon walk">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <div class="metric-content">
              <span class="metric-value">{{ dailySummary.walkTime }}<small>분</small></span>
              <span class="metric-label">산책 시간</span>
            </div>
            <div class="metric-progress">
              <div class="progress-bar">
                <div class="progress-fill walk" :style="{ width: walkProgress + '%' }"></div>
              </div>
              <span class="progress-text">목표 60분</span>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-icon distance">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
            </div>
            <div class="metric-content">
              <span class="metric-value">{{ dailySummary.distance }}<small>km</small></span>
              <span class="metric-label">이동 거리</span>
            </div>
            <div class="metric-progress">
              <div class="progress-bar">
                <div class="progress-fill distance" :style="{ width: distanceProgress + '%' }"></div>
              </div>
              <span class="progress-text">목표 2km</span>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-icon activity">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
            </div>
            <div class="metric-content">
              <span class="metric-value">{{ dailySummary.activities }}<small>회</small></span>
              <span class="metric-label">활동 횟수</span>
            </div>
            <div class="metric-progress">
              <div class="progress-bar">
                <div class="progress-fill activity" :style="{ width: activityProgress + '%' }"></div>
              </div>
              <span class="progress-text">목표 10회</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 이상 감지 알림 -->
      <section class="alerts-section">
        <div class="section-header">
          <h3 class="section-title">이상 감지 알림</h3>
          <span class="alert-count" :class="{ warning: dailySummary.alerts > 0 }">{{ dailySummary.alerts }}건</span>
        </div>

        <div v-if="dailySummary.alerts === 0" class="empty-alerts">
          <div class="empty-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <p>오늘은 이상 감지 알림이 없습니다</p>
        </div>

        <div v-else class="alert-list">
          <div v-for="(alert, index) in recentAlerts" :key="index" class="alert-item">
            <div class="alert-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </div>
            <div class="alert-content">
              <span class="alert-message">{{ alert.msg }}</span>
              <span class="alert-time">{{ alert.time }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 건강 팁 -->
      <section class="tips-section">
        <h3 class="section-title">오늘의 건강 팁</h3>
        <div class="tip-card">
          <div class="tip-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="16" x2="12" y2="12"/>
              <line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>
          </div>
          <div class="tip-content">
            <p class="tip-text">{{ healthTip }}</p>
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
import { activityApi } from '@/api';

const robotStore = useRobotStore();

// 오늘 날짜
const formattedDate = computed(() => {
  return new Date().toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'short'
  });
});

// 일일 요약 데이터
const dailySummary = ref({
  walkTime: 0,
  distance: 0,
  activities: 0,
  alerts: 0
});

// 최근 알림
const recentAlerts = ref([]);

// 건강 점수 계산
const healthScore = computed(() => {
  const walkScore = Math.min(dailySummary.value.walkTime / 60 * 40, 40);
  const distanceScore = Math.min(dailySummary.value.distance / 2 * 30, 30);
  const activityScore = Math.min(dailySummary.value.activities / 10 * 30, 30);
  return Math.round(walkScore + distanceScore + activityScore);
});

const healthScoreClass = computed(() => {
  if (healthScore.value >= 80) return 'excellent';
  if (healthScore.value >= 60) return 'good';
  if (healthScore.value >= 40) return 'fair';
  return 'poor';
});

const healthMessage = computed(() => {
  if (healthScore.value >= 80) return '오늘 활동량이 충분합니다!';
  if (healthScore.value >= 60) return '조금만 더 활동해 보세요!';
  if (healthScore.value >= 40) return '산책 시간을 늘려보세요';
  return '오늘 활동을 시작해 보세요!';
});

// 진행률 계산
const walkProgress = computed(() => Math.min((dailySummary.value.walkTime / 60) * 100, 100));
const distanceProgress = computed(() => Math.min((dailySummary.value.distance / 2) * 100, 100));
const activityProgress = computed(() => Math.min((dailySummary.value.activities / 10) * 100, 100));

// 건강 팁
const healthTips = [
  '규칙적인 산책은 심혈관 건강에 도움이 됩니다.',
  '하루 30분 이상의 활동이 권장됩니다.',
  '충분한 휴식도 건강 유지에 중요합니다.',
  '꾸준한 활동이 치매 예방에 도움이 됩니다.',
  '적절한 수분 섭취를 잊지 마세요.'
];

const healthTip = ref(healthTips[Math.floor(Math.random() * healthTips.length)]);

// 데이터 로드
const loadData = async () => {
  try {
    // API에서 오늘 요약 정보 가져오기
    const summaryRes = await activityApi.getTodaySummary();
    dailySummary.value = {
      walkTime: summaryRes.data.walkTime || 0,
      distance: summaryRes.data.distance || 0,
      activities: summaryRes.data.activities || 0,
      alerts: summaryRes.data.alerts || 0
    };

    // 오늘 로그에서 warning 타입만 가져오기
    const logsRes = await activityApi.getTodayLogs();
    recentAlerts.value = logsRes.data
      .filter(log => log.type === 'warning')
      .slice(0, 5);
  } catch (e) {
    console.error('헬스케어 데이터 로드 실패:', e);
  }
};

onMounted(() => {
  robotStore.connectWebSocket();
  loadData();
});

onUnmounted(() => {
  robotStore.disconnectWebSocket();
});

// WebSocket 실시간 데이터 반영
const unwatch = robotStore.$subscribe((mutation, state) => {
  if (state.dailySummary) {
    dailySummary.value = {
      ...dailySummary.value,
      walkTime: state.dailySummary.walkTime || dailySummary.value.walkTime,
      alerts: state.dailySummary.alerts || dailySummary.value.alerts
    };
  }
});

onUnmounted(() => {
  if (typeof unwatch === 'function') unwatch();
});
</script>

<style scoped>
.healthcare-view {
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

/* 요약 섹션 */
.summary-section {
  margin-top: 16px;
}

.summary-card {
  background: linear-gradient(135deg, #EF4444 0%, #F87171 100%);
  border-radius: 20px;
  padding: 24px;
  color: white;
}

.summary-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}

.summary-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.summary-title h2 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 2px;
}

.summary-date {
  font-size: 13px;
  opacity: 0.8;
}

.health-score {
  display: flex;
  align-items: center;
  gap: 20px;
}

.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-circle.excellent {
  background: rgba(34, 197, 94, 0.3);
}

.score-circle.good {
  background: rgba(59, 130, 246, 0.3);
}

.score-circle.fair {
  background: rgba(245, 158, 11, 0.3);
}

.score-circle.poor {
  background: rgba(239, 68, 68, 0.3);
}

.score-value {
  font-size: 28px;
  font-weight: 700;
}

.score-label {
  font-size: 12px;
  opacity: 0.8;
}

.score-message {
  flex: 1;
  font-size: 15px;
  font-weight: 500;
  line-height: 1.5;
}

/* 지표 섹션 */
.metrics-section {
  margin-top: 28px;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 14px;
}

.metrics-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 16px;
}

.metric-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.metric-icon.walk {
  background: var(--primary-light);
  color: var(--primary);
}

.metric-icon.distance {
  background: var(--success-light);
  color: var(--success);
}

.metric-icon.activity {
  background: var(--warning-light);
  color: var(--warning);
}

.metric-content {
  flex: 1;
  min-width: 0;
}

.metric-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.metric-value small {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
}

.metric-label {
  font-size: 13px;
  color: var(--text-tertiary);
}

.metric-progress {
  width: 100px;
  flex-shrink: 0;
}

.progress-bar {
  height: 6px;
  background: var(--gray-100);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

.progress-fill.walk {
  background: var(--primary);
}

.progress-fill.distance {
  background: var(--success);
}

.progress-fill.activity {
  background: var(--warning);
}

.progress-text {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-top: 4px;
  display: block;
  text-align: right;
}

/* 알림 섹션 */
.alerts-section {
  margin-top: 28px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.alert-count {
  font-size: 14px;
  font-weight: 600;
  color: var(--success);
}

.alert-count.warning {
  color: var(--warning);
}

.empty-alerts {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 32px 16px;
  text-align: center;
}

.empty-icon {
  width: 56px;
  height: 56px;
  background: var(--success-light);
  color: var(--success);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
}

.empty-alerts p {
  font-size: 14px;
  color: var(--text-tertiary);
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--bg-primary);
  border-radius: 14px;
  padding: 14px 16px;
}

.alert-icon {
  width: 36px;
  height: 36px;
  background: var(--warning-light);
  color: var(--warning);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-message {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.alert-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

/* 팁 섹션 */
.tips-section {
  margin-top: 28px;
}

.tip-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 18px;
}

.tip-icon {
  width: 44px;
  height: 44px;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.tip-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  line-height: 1.6;
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
