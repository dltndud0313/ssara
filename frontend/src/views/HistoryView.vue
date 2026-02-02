<template>
  <div class="history">
    <header class="header">
      <h1 class="header-title">활동 기록</h1>
      <button class="filter-btn" @click="showFilter = !showFilter">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
        </svg>
      </button>
    </header>

    <!-- 2주 달력 -->
    <div class="calendar-section">
      <div class="calendar-header">
        <span class="calendar-title">최근 2주</span>
        <span class="selected-date-label">{{ formatFullDate(selectedDate) }}</span>
      </div>

      <!-- 요일 헤더 -->
      <div class="weekday-header">
        <span v-for="day in weekdays" :key="day" class="weekday">{{ day }}</span>
      </div>

      <!-- 2주 달력 그리드 -->
      <div class="calendar-grid">
        <template v-for="(date, index) in calendarDates" :key="index">
          <!-- 빈 칸 (요일 맞추기용) -->
          <div v-if="!date" class="calendar-day empty"></div>
          <!-- 날짜 버튼 -->
          <button
            v-else
            class="calendar-day"
            :class="{
              selected: isSameDay(date, selectedDate),
              today: isSameDay(date, new Date()),
              'other-month': date.getMonth() !== new Date().getMonth()
            }"
            @click="selectCalendarDate(date)"
          >
            <span class="day-number">{{ date.getDate() }}</span>
            <span class="month-label" v-if="date.getDate() === 1 || isFirstValidDate(index)">{{ date.getMonth() + 1 }}월</span>
          </button>
        </template>
      </div>
    </div>

    <!-- 필터 패널 -->
    <div v-if="showFilter" class="filter-panel">
      <div class="filter-chips">
        <button
          v-for="filter in filters"
          :key="filter.value"
          class="filter-chip"
          :class="{ active: selectedFilter === filter.value }"
          @click="selectedFilter = filter.value"
        >
          {{ filter.label }}
        </button>
      </div>
    </div>

    <main class="content">
      <!-- 선택된 날짜 요약 카드 -->
      <section class="summary-card">
        <div class="summary-header">
          <span class="summary-label">{{ isToday ? '오늘의 활동' : formatDisplayDate(selectedDate) + ' 활동' }}</span>
          <span class="summary-date">{{ formatWeekday(selectedDate) }}</span>
        </div>
        <div class="summary-stats">
          <div class="stat-item">
            <div class="stat-icon walk">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M13 4v16M7 4v16M3 8l4-4 4 4M13 20l4-4 4 4"/>
              </svg>
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ selectedSummary.walkTime }}분</span>
              <span class="stat-label">산책 시간</span>
            </div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-icon events">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
              </svg>
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ selectedSummary.totalEvents }}건</span>
              <span class="stat-label">알림</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 활동 로그 목록 -->
      <section class="log-section">
        <div class="section-header">
          <h3 class="section-title">{{ formatSectionTitle(selectedDate) }}</h3>
          <span class="section-date">{{ formatFullDate(selectedDate) }}</span>
        </div>

        <div class="log-list">
          <div v-if="loading" class="empty-state">
            <p>로딩 중...</p>
          </div>
          <div v-else-if="filteredLogs.length === 0" class="empty-state">
            <p>{{ formatDisplayDate(selectedDate) }} 기록이 없습니다.</p>
          </div>
          <div
            v-else
            v-for="(log, index) in filteredLogs"
            :key="index"
            class="log-item"
          >
            <div class="log-icon" :class="log.type">
              <component :is="getIcon(log.type)" />
            </div>
            <div class="log-content">
              <span class="log-message">{{ log.msg }}</span>
              <span class="log-detail" v-if="log.detail">{{ log.detail }}</span>
            </div>
            <span class="log-time">{{ log.time }}</span>
          </div>
        </div>
      </section>

      <div class="bottom-spacer"></div>
    </main>

    <!-- 날짜 선택 모달 -->
    <div v-if="showDatePicker" class="modal-overlay" @click="showDatePicker = false">
      <div class="date-picker-modal" @click.stop>
        <div class="modal-header">
          <h3>날짜 선택</h3>
          <button class="modal-close" @click="showDatePicker = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="calendar-input">
          <input
            type="date"
            :value="formatDateForInput(selectedDate)"
            :min="formatDateForInput(minSelectableDate)"
            :max="formatDateForInput(new Date())"
            @change="onDateSelect"
          />
          <p class="date-hint">최근 2주간의 기록만 확인할 수 있습니다.</p>
        </div>
        <div class="recent-dates">
          <p class="recent-label">최근 2주</p>
          <div class="recent-list">
            <button
              v-for="date in recentDates"
              :key="date.toISOString()"
              class="recent-date-btn"
              :class="{ active: isSameDay(date, selectedDate) }"
              @click="selectDate(date)"
            >
              {{ formatRecentDate(date) }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 하단 네비게이션 -->
    <nav class="bottom-nav">
      <button class="nav-item" @click="$router.push('/home')">
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
      <button class="nav-item active">
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
import { ref, computed, h, onMounted, onUnmounted, watch } from 'vue';
import { activityApi } from '../api';
import { useRobotStore } from '@/stores/robotStore';

const robotStore = useRobotStore();

const showFilter = ref(false);
const showDatePicker = ref(false);
const selectedFilter = ref('all');
const loading = ref(true);
const selectedDate = ref(new Date());

// 요일 배열
const weekdays = ['일', '월', '화', '수', '목', '금', '토'];

const filters = [
  { label: '전체', value: 'all' },
  { label: '정보', value: 'info' },
  { label: '주의', value: 'warning' },
  { label: '활동', value: 'action' }
];

const selectedSummary = ref({
  totalEvents: 0,
  walkTime: 0,
  alerts: 0,
  distance: 0
});

// 선택된 날짜의 로그
const selectedLogs = ref([]);

// 최대 조회 가능 기간 (2주 = 14일)
const MAX_DAYS = 14;

// 2주 달력 날짜 배열 (요일에 맞춰 정렬)
const calendarDates = computed(() => {
  const result = [];
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // 2주 전 날짜 계산
  const startDate = new Date(today);
  startDate.setDate(today.getDate() - (MAX_DAYS - 1));

  // 시작 날짜의 요일 (0=일요일, 6=토요일)
  const startDayOfWeek = startDate.getDay();

  // 첫 주 시작 전 빈 칸 추가 (요일 맞추기)
  for (let i = 0; i < startDayOfWeek; i++) {
    result.push(null);
  }

  // 14일 날짜 추가
  for (let i = 0; i < MAX_DAYS; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);
    result.push(date);
  }

  return result;
});

// 최근 14일 날짜 목록 (최신순)
const recentDates = computed(() => {
  const dates = [];
  const today = new Date();
  for (let i = 0; i < MAX_DAYS; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    dates.push(date);
  }
  return dates;
});

// 2주 전 날짜 (최소 선택 가능 날짜)
const minSelectableDate = computed(() => {
  const date = new Date();
  date.setDate(date.getDate() - (MAX_DAYS - 1));
  date.setHours(0, 0, 0, 0);
  return date;
});

// 오늘인지 확인
const isToday = computed(() => {
  const today = new Date();
  return isSameDay(selectedDate.value, today);
});

// 어제인지 확인
const isYesterday = computed(() => {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  return isSameDay(selectedDate.value, yesterday);
});

// 2주 전인지 확인
const isTwoWeeksAgo = computed(() => {
  const twoWeeksAgo = new Date();
  twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 13);
  return isSameDay(selectedDate.value, twoWeeksAgo);
});

// 가장 오래된 날짜인지 확인 (더 이전으로 이동 불가)
const isOldestDate = computed(() => {
  return selectedDate.value <= minSelectableDate.value;
});

// 필터링된 로그 (오늘이면 WebSocket 로그 포함)
const filteredLogs = computed(() => {
  let logs = selectedLogs.value;

  // 오늘이면 WebSocket에서 받은 실시간 로그도 포함
  if (isToday.value && robotStore.activityLogs.length > 0) {
    logs = [...robotStore.activityLogs, ...logs];
  }

  if (selectedFilter.value === 'all') return logs;
  return logs.filter(log => log.type === selectedFilter.value);
});

// 날짜 비교 함수
function isSameDay(date1, date2) {
  return date1.getFullYear() === date2.getFullYear() &&
         date1.getMonth() === date2.getMonth() &&
         date1.getDate() === date2.getDate();
}

// 첫 번째 유효한 날짜인지 확인 (월 라벨 표시용)
function isFirstValidDate(index) {
  // 이전 인덱스에 날짜가 없으면 첫 번째 유효한 날짜
  for (let i = 0; i < index; i++) {
    if (calendarDates.value[i] !== null) {
      return false;
    }
  }
  return true;
}

// 날짜 포맷 함수들
function formatDisplayDate(date) {
  return date.toLocaleDateString('ko-KR', {
    month: 'long', day: 'numeric'
  });
}

function formatWeekday(date) {
  return date.toLocaleDateString('ko-KR', { weekday: 'short' });
}

function formatFullDate(date) {
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric', month: 'long', day: 'numeric'
  });
}

function formatSectionTitle(date) {
  if (isToday.value) return '오늘';
  if (isYesterday.value) return '어제';
  return formatDisplayDate(date);
}

function formatDateForInput(date) {
  return date.toISOString().split('T')[0];
}

function formatRecentDate(date) {
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);

  if (isSameDay(date, today)) return '오늘';
  if (isSameDay(date, yesterday)) return '어제';
  return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric', weekday: 'short' });
}

function formatDateForApi(date) {
  return date.toISOString().split('T')[0];
}

// 날짜 변경 함수
function changeDate(offset) {
  const newDate = new Date(selectedDate.value);
  newDate.setDate(newDate.getDate() + offset);

  // 미래 날짜는 선택 불가
  if (newDate > new Date()) return;

  // 2주 이전 날짜는 선택 불가
  if (newDate < minSelectableDate.value) return;

  selectedDate.value = newDate;
}

function goToToday() {
  selectedDate.value = new Date();
}

function goToYesterday() {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  selectedDate.value = yesterday;
}

function goToTwoWeeksAgo() {
  const twoWeeksAgo = new Date();
  twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 13); // 오늘 포함 14일
  selectedDate.value = twoWeeksAgo;
}

function selectDate(date) {
  // 2주 이전 날짜는 선택 불가
  if (date < minSelectableDate.value) return;
  selectedDate.value = new Date(date);
  showDatePicker.value = false;
}

// 달력에서 날짜 선택
function selectCalendarDate(date) {
  selectedDate.value = new Date(date);
}

function onDateSelect(event) {
  const date = new Date(event.target.value);
  // 2주 이전 날짜는 선택 불가
  if (date < minSelectableDate.value) {
    alert('최근 2주간의 기록만 확인할 수 있습니다.');
    return;
  }
  selectedDate.value = date;
  showDatePicker.value = false;
}

// 데이터 로드
const fetchActivityData = async () => {
  loading.value = true;
  try {
    const dateStr = formatDateForApi(selectedDate.value);

    let logsResponse;
    if (isToday.value) {
      logsResponse = await activityApi.getTodayLogs();
    } else if (isYesterday.value) {
      logsResponse = await activityApi.getYesterdayLogs();
    } else {
      logsResponse = await activityApi.getLogsByDate(dateStr);
    }

    selectedLogs.value = logsResponse.data;

    // 요약 정보: 오늘이면 실시간 WebSocket 데이터, 아니면 API 로그 기반 계산
    const logs = logsResponse.data;
    if (isToday.value && robotStore.dailySummary.walkTime > 0) {
      // 오늘: WebSocket 실시간 데이터 사용
      selectedSummary.value = {
        totalEvents: robotStore.dailySummary.totalEvents || logs.length,
        walkTime: robotStore.dailySummary.walkTime,
        distance: robotStore.dailySummary.distance || 0,
        alerts: robotStore.dailySummary.alerts
      };
    } else {
      // 과거: API 로그 기반 계산
      selectedSummary.value = {
        totalEvents: logs.length,
        walkTime: logs.filter(l => l.type === 'action').length * 5,
        distance: (logs.length * 0.1).toFixed(1),
        alerts: logs.filter(l => l.type === 'warning').length
      };
    }
  } catch (error) {
    console.error('활동 기록 조회 실패:', error);
    selectedLogs.value = [];
  } finally {
    loading.value = false;
  }
};

// 날짜 변경 시 데이터 다시 로드
watch(selectedDate, () => {
  fetchActivityData();
});

// WebSocket에서 실시간 요약 데이터 받으면 업데이트 (오늘만)
watch(() => robotStore.dailySummary, (newSummary) => {
  if (isToday.value && newSummary.walkTime > 0) {
    selectedSummary.value = {
      ...selectedSummary.value,
      walkTime: newSummary.walkTime,
      alerts: newSummary.alerts,
      totalEvents: newSummary.totalEvents || selectedSummary.value.totalEvents
    };
  }
}, { deep: true });

onMounted(() => {
  robotStore.connectWebSocket();
  fetchActivityData();
});

onUnmounted(() => {
  robotStore.disconnectWebSocket();
});

// 아이콘 컴포넌트
const getIcon = (type) => {
  const icons = {
    info: () => h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('circle', { cx: 12, cy: 12, r: 10 }),
      h('line', { x1: 12, y1: 16, x2: 12, y2: 12 }),
      h('line', { x1: 12, y1: 8, x2: 12.01, y2: 8 })
    ]),
    warning: () => h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('path', { d: 'M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z' }),
      h('line', { x1: 12, y1: 9, x2: 12, y2: 13 }),
      h('line', { x1: 12, y1: 17, x2: 12.01, y2: 17 })
    ]),
    action: () => h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('polygon', { points: '13 2 3 14 12 14 11 22 21 10 12 10 13 2' })
    ])
  };
  return icons[type] || icons.info;
};
</script>

<style scoped>
.history {
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
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.filter-btn {
  width: 40px;
  height: 40px;
  background: var(--bg-tertiary);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: background 0.2s;
}

.filter-btn:active {
  background: var(--gray-200);
}

/* 2주 달력 */
.calendar-section {
  background: var(--bg-primary);
  padding: 16px 20px 20px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.calendar-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-secondary);
}

.selected-date-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary);
}

.weekday-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 8px;
}

.weekday {
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  padding: 4px 0;
}

.weekday:first-child {
  color: #EF4444;
}

.weekday:last-child {
  color: var(--primary);
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: var(--bg-tertiary);
  transition: all 0.2s;
  position: relative;
  min-height: 44px;
}

.calendar-day.empty {
  background: transparent;
  pointer-events: none;
}

.calendar-day:active {
  transform: scale(0.95);
}

.calendar-day .day-number {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.calendar-day .month-label {
  font-size: 9px;
  color: var(--text-tertiary);
  position: absolute;
  top: 4px;
  left: 50%;
  transform: translateX(-50%);
}

.calendar-day.today {
  background: var(--gray-200);
}

.calendar-day.today .day-number {
  color: var(--text-primary);
}

.calendar-day.today::after {
  content: '';
  position: absolute;
  bottom: 6px;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--primary);
}

.calendar-day.selected {
  background: var(--primary);
}

.calendar-day.selected .day-number {
  color: white;
}

.calendar-day.selected .month-label {
  color: rgba(255, 255, 255, 0.7);
}

.calendar-day.selected::after {
  display: none;
}

.calendar-day.other-month .day-number {
  color: var(--text-tertiary);
}

/* 기존 날짜 선택 (삭제됨, 호환성용 유지) */
.date-selector {
  display: none;
}

.date-nav-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.date-nav-btn:active:not(:disabled) {
  background: var(--gray-200);
}

.date-nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.date-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--bg-tertiary);
  border-radius: 20px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  transition: background 0.2s;
}

.date-display:active {
  background: var(--gray-200);
}

.date-display svg {
  color: var(--primary);
}

/* 빠른 날짜 선택 (달력으로 대체됨) */
.quick-dates {
  display: none;
}

.quick-date-chip {
  padding: 8px 16px;
  border-radius: 20px;
  background: var(--bg-tertiary);
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.quick-date-chip.active {
  background: var(--primary);
  color: white;
}

/* 필터 패널 */
.filter-panel {
  background: var(--bg-primary);
  padding: 12px 20px 16px;
  border-bottom: 1px solid var(--gray-100);
}

.filter-chips {
  display: flex;
  gap: 8px;
}

.filter-chip {
  padding: 8px 16px;
  border: 1px solid var(--gray-200);
  border-radius: 20px;
  background: var(--bg-primary);
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.filter-chip.active {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.content {
  padding: 0 20px 20px;
}

/* 요약 카드 */
.summary-card {
  background: var(--bg-primary);
  border-radius: 20px;
  padding: 20px;
  margin-top: 20px;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.summary-label {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
}

.summary-date {
  font-size: 13px;
  color: var(--text-tertiary);
}

.summary-stats {
  display: flex;
  align-items: center;
}

.stat-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: var(--gray-100);
  margin: 0 12px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.walk {
  background: var(--primary-light);
  color: var(--primary);
}

.stat-icon.distance {
  background: var(--success-light);
  color: var(--success);
}

.stat-icon.events {
  background: var(--warning-light);
  color: var(--warning);
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

/* 로그 섹션 */
.log-section {
  margin-top: 28px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
}

.section-date {
  font-size: 13px;
  color: var(--text-tertiary);
}

.log-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 28px;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 16px;
}

.log-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.log-icon.info {
  background: var(--success-light);
  color: var(--success);
}

.log-icon.warning {
  background: var(--warning-light);
  color: var(--warning);
}

.log-icon.action {
  background: var(--primary-light);
  color: var(--primary);
}

.log-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.log-message {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
}

.log-detail {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

.log-time {
  font-size: 13px;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.bottom-spacer {
  height: 20px;
}

.empty-state {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 32px 16px;
  text-align: center;
  color: var(--text-tertiary);
  font-size: 14px;
}

/* 날짜 선택 모달 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
}

.date-picker-modal {
  background: var(--bg-primary);
  border-radius: 20px 20px 0 0;
  width: 100%;
  max-width: 600px;
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-close {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.calendar-input {
  margin-bottom: 24px;
}

.calendar-input input {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid var(--gray-200);
  border-radius: 12px;
  font-size: 16px;
  color: var(--text-primary);
  background: var(--bg-primary);
}

.date-hint {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 8px;
  text-align: center;
}

.recent-dates {
  margin-bottom: 20px;
}

.recent-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-tertiary);
  margin-bottom: 12px;
}

.recent-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.recent-date-btn {
  padding: 10px 16px;
  border-radius: 12px;
  background: var(--bg-tertiary);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.recent-date-btn.active {
  background: var(--primary);
  color: white;
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
