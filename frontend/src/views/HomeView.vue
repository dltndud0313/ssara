<template>
  <div class="home-container">
    <header class="header">
      <h1 class="robot-name">해피 (GAE-001)</h1>
      <div class="header-right">
        <div class="status-badge">
          <span class="dot"></span> 실시간 연결됨
        </div>

        <button class="icon-btn" @click="handleLogout" title="로그아웃">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
        </button>

        <button class="noti-btn">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
          <span class="noti-dot"></span>
        </button>
      </div>
    </header>

    <main class="content-scroll">
      
      <section class="hero-card">
        <div class="hero-header">
          <div>
            <h2 class="hero-title">오늘의 안심 리포트</h2>
            <p class="hero-subtitle">오늘도 안전하게 지켜드렸어요!</p>
          </div>
          <div class="robot-img">🐕</div>
        </div>

        <div class="stats-row">
          <div class="stat-item">
            <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
            <span class="stat-label">산책</span>
            <span class="stat-value">45분</span>
          </div>
          <div class="stat-item">
            <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
            <span class="stat-label">위험 감지</span>
            <span class="stat-value">0회</span>
          </div>
          <div class="stat-item">
            <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><line x1="16" y1="21" x2="16" y2="7"></line></svg>
            <span class="stat-label">배터리</span>
            <span class="stat-value">충분</span>
          </div>
        </div>

        <div class="mini-map">
          <span class="pin">📍</span>
          <div class="map-text">
            <span class="label">현재 위치</span>
            <span class="address">{{ robotState.location }}</span>
            <span class="sub-link">최근 경로 표시</span>
          </div>
        </div>
      </section>

      <section class="status-grid">
        <div class="grid-card">
          <div class="card-icon-circle blue-bg">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6A67CE" stroke-width="2"><rect x="1" y="6" width="18" height="12" rx="2" ry="2"></rect><line x1="23" y1="13" x2="23" y2="11"></line></svg>
          </div>
          <div class="card-content">
            <span class="big-value">{{ robotState.battery }}%</span>
            <span class="label">배터리</span>
            <span class="sub-text">약 4시간 남음</span>
          </div>
        </div>

        <div class="grid-card">
          <div class="top-row">
            <div class="card-icon-circle green-bg">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#03C75A" stroke-width="2"><circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline></svg>
            </div>
            <svg class="trend-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#03C75A" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
          </div>
          <div class="card-content">
            <span class="big-value">98점</span>
            <span class="label">안전 점수</span>
            <span class="sub-text green-text">매우 좋음</span>
          </div>
        </div>

        <div class="grid-card wide">
          <div class="flex-row">
            <div class="card-icon-circle yellow-bg">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFC107" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
            </div>
            <div class="mode-text">
              <span class="label-bold">활동 모드</span>
              <span class="sub-text">대기 중</span>
            </div>
          </div>
          <span class="status-pill">정상</span>
        </div>
      </section>

      <section class="recent-activity">
        <div class="section-header">
          <h3>최근 활동 내역</h3>
          <span class="more-link">더보기 ></span>
        </div>

        <div class="activity-list">
          <div v-for="(log, index) in robotState.logs" :key="index" class="activity-item">
            <div class="icon-box" :class="{
              'green': log.type === 'info', 
              'yellow': log.type === 'warning',
              'blue': log.type === 'action'
            }">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
            </div>
            <div class="item-info">
              <span class="item-title">{{ log.msg }}</span>
              <span class="item-time">{{ log.time }}</span>
            </div>
          </div>
        </div>
      </section>

      <div class="spacer"></div>
    </main>

    <nav class="bottom-nav">
      <div class="nav-item active">
        <div class="nav-icon-bg">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
        </div>
        <span>홈</span>
      </div>
      <div class="nav-item">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
        <span>위치</span>
      </div>
      <div class="nav-item">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
        <span>기록</span>
      </div>
      <div class="nav-item">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
        <span>설정</span>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { robotState } from '../store.js'; // 상태 저장소 (배터리 등)

const router = useRouter();

// 로그아웃 기능
const handleLogout = () => {
  if (confirm("정말 로그아웃 하시겠습니까?")) {
    localStorage.removeItem('accessToken'); // 저장된 토큰 삭제
    router.push('/'); // 로그인 화면으로 이동
  }
};
</script>

<style scoped>
/* 전체 컨테이너 */
.home-container {
  height: 100vh;
  background-color: #F7F8FA; /* 밝은 회색 배경 */
  display: flex;
  flex-direction: column;
  position: relative;
  font-family: 'Pretendard', sans-serif;
}

/* 1. 헤더 */
.header {
  background-color: white;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 10;
}

.robot-name {
  font-size: 18px;
  font-weight: 800;
  color: #333;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px; /* 버튼 간격 살짝 조정 */
}

.status-badge {
  background-color: #EDFDF4; /* 연한 초록 배경 */
  color: #03C75A;
  font-size: 12px;
  font-weight: 700;
  padding: 6px 10px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 5px;
  margin-right: 8px; /* 버튼과 간격 */
}

.dot {
  width: 8px;
  height: 8px;
  background-color: #03C75A;
  border-radius: 50%;
  display: block;
}

/* [추가] 로그아웃 버튼 등 아이콘 버튼 공통 */
.icon-btn, .noti-btn {
  background: none;
  border: none;
  position: relative;
  padding: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.icon-btn:active, .noti-btn:active {
  transform: scale(0.9);
}

.noti-dot {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 6px;
  height: 6px;
  background-color: #FF3B30;
  border-radius: 50%;
  border: 1px solid white;
}

/* 스크롤 영역 */
.content-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  /* 스크롤바 숨기기 */
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.content-scroll::-webkit-scrollbar { display: none; }

/* 2. Hero Card (보라색 리포트) */
.hero-card {
  background-color: #6A67CE;
  border-radius: 24px;
  padding: 24px;
  color: white;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 20px rgba(106, 103, 206, 0.3);
}

.hero-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.hero-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 5px 0;
}

.hero-subtitle {
  font-size: 13px;
  opacity: 0.8;
  margin: 0;
}

.robot-img {
  font-size: 40px; /* 이미지 대신 이모지 */
  background: rgba(255, 255, 255, 0.2);
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 통계 Row */
.stats-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 20px;
}

.stat-item {
  flex: 1;
  background-color: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 12px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.stat-icon { width: 20px; height: 20px; margin-bottom: 6px; opacity: 0.9; }

.stat-label { font-size: 11px; opacity: 0.8; margin-bottom: 2px; }
.stat-value { font-size: 14px; font-weight: 700; }

/* 미니맵 */
.mini-map {
  background-color: #EDF3EC; /* 연한 연두색/베이지 */
  border-radius: 16px;
  padding: 15px;
  display: flex;
  align-items: center;
  color: #333;
}

.pin { font-size: 16px; margin-right: 10px; }

.map-text { display: flex; flex-direction: column; }
.map-text .label { font-size: 11px; color: #03C75A; font-weight: 600; }
.map-text .address { font-size: 14px; font-weight: 700; color: #555; margin: 2px 0; }
.map-text .sub-link { font-size: 11px; color: #999; }

/* 3. 상태 그리드 */
.status-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 30px;
}

.grid-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 10px rgba(0,0,0,0.02);
}

.grid-card.wide {
  grid-column: span 2;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
}

.card-icon-circle {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 12px;
}

.blue-bg { background-color: #EEF4FF; }
.green-bg { background-color: #E8F9EE; }
.yellow-bg { background-color: #FFF8E1; }

.top-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}
.card-icon-circle { margin-bottom: 0; } /* override */

.card-content { display: flex; flex-direction: column; margin-top: 10px; }

.big-value { font-size: 22px; font-weight: 800; color: #333; line-height: 1.2; }
.label { font-size: 13px; color: #666; font-weight: 600; margin-bottom: 4px; }
.sub-text { font-size: 11px; color: #999; }
.green-text { color: #03C75A; font-weight: 600; }

/* Wide Card styles */
.flex-row { display: flex; align-items: center; gap: 12px; }
.mode-text { display: flex; flex-direction: column; }
.label-bold { font-size: 14px; font-weight: 700; color: #333; }
.status-pill {
  background-color: #FFF8E1;
  color: #DFA40F;
  font-size: 12px;
  font-weight: 700;
  padding: 6px 14px;
  border-radius: 20px;
}

/* 4. 최근 활동 내역 */
.recent-activity { margin-bottom: 20px; }

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 { font-size: 16px; font-weight: 700; color: #333; margin: 0; }
.more-link { font-size: 13px; color: #6A67CE; cursor: pointer; }

.activity-list { display: flex; flex-direction: column; gap: 12px; }

.activity-item {
  background: white;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.icon-box {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 14px;
}
.icon-box.green { background-color: #E3F8E8; color: #03C75A; }
.icon-box.blue { background-color: #E8F0FE; color: #6A67CE; }
.icon-box.yellow { background-color: #FFF8E1; color: #FBC02D; }
/* SVG 스트로크 색상 상속 */
.icon-box svg { stroke: currentColor; }

.item-info { flex: 1; display: flex; flex-direction: column; }
.item-title { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 2px; }
.item-time { font-size: 12px; color: #999; }

.spacer { height: 80px; }

/* 5. 하단 탭바 */
.bottom-nav {
  position: fixed;
  bottom: 0;
  width: 100%;
  max-width: 600px; /* PC화면 대응 */
  background: white;
  height: 70px;
  display: flex;
  justify-content: space-around;
  align-items: center;
  border-top: 1px solid #EEE;
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
  box-shadow: 0 -4px 20px rgba(0,0,0,0.03);
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #CCC;
  font-size: 10px;
  gap: 4px;
  cursor: pointer;
  width: 60px;
}

.nav-item svg { width: 22px; height: 22px; }

.nav-item.active { color: #6A67CE; font-weight: 700; }
.nav-item.active .nav-icon-bg {
  background-color: #EEF0FF;
  width: 40px;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 12px;
  margin-bottom: -2px; /* 위치 보정 */
}
</style>