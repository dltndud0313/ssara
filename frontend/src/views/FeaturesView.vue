<template>
  <div class="features-page">
    <!-- Features Grid -->
    <section class="features-section">
      <div class="features-container">
        <div class="section-header">
          <h2 class="section-title">주요 기능</h2>
          <p class="section-desc">우리 아이를 위한 스마트 케어 솔루션</p>
        </div>

        <div class="features-grid">
          <!-- Healthcare Card -->
          <article class="feature-card" @click="$router.push('/healthcare')">
            <div class="card-badge">HEALTH</div>
            <div class="card-inner">
              <h3 class="card-title">헬스케어</h3>
              <p class="card-description">
                AI 기반 건강 모니터링으로<br/>반려견의 건강을 체계적으로 관리하세요.
              </p>
              <div class="card-buttons">
                <span class="btn-learn">
                  자세히 보기
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                  </svg>
                </span>
              </div>
            </div>
            <div class="card-image-wrapper">
              <img
                src="https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=600&q=80"
                alt="Healthcare"
                class="card-image"
                loading="lazy"
              />
            </div>
          </article>

          <!-- AI Assistant Card -->
          <article class="feature-card" @click="$router.push('/ai-assistant')">
            <div class="card-badge ai">AI</div>
            <div class="card-inner">
              <h3 class="card-title">AI 비서</h3>
              <p class="card-description">
                AI 비서에게 반려견 관련<br/>궁금한 점을 물어보세요.
              </p>
              <div class="card-buttons">
                <span class="btn-learn">
                  자세히 보기
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                  </svg>
                </span>
              </div>
            </div>
            <div class="card-image-wrapper">
              <img
                src="https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&q=80"
                alt="AI Assistant"
                class="card-image"
                loading="lazy"
              />
            </div>
          </article>
        </div>

        <!-- Second Row -->
        <div class="features-grid">
          <!-- Memo Card -->
          <article class="feature-card" @click="$router.push('/memo')">
            <div class="card-badge memo">MEMO</div>
            <div class="card-inner">
              <h3 class="card-title">메모장</h3>
              <p class="card-description">
                반려견 관련 메모를<br/>간편하게 기록하고 관리하세요.
              </p>
              <div class="card-buttons">
                <span class="btn-learn">
                  자세히 보기
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                  </svg>
                </span>
              </div>
            </div>
            <div class="card-image-wrapper">
              <img
                src="https://images.unsplash.com/photo-1517842645767-c639042777db?w=600&q=80"
                alt="Memo"
                class="card-image"
                loading="lazy"
              />
            </div>
          </article>

          <!-- Community Card -->
          <article class="feature-card dark" @click="$router.push('/community')">
            <div class="card-badge community">COMMUNITY</div>
            <div class="card-inner">
              <h3 class="card-title">커뮤니티</h3>
              <p class="card-description">
                다른 반려인들과 정보를 공유하고<br/>소통해보세요.
              </p>
              <div class="card-buttons">
                <span class="btn-learn light">
                  자세히 보기
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                  </svg>
                </span>
              </div>
            </div>
            <div class="card-image-wrapper">
              <img
                src="https://images.unsplash.com/photo-1516734212186-a967f81ad0d7?w=600&q=80"
                alt="Community"
                class="card-image"
                loading="lazy"
              />
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- Bottom Spacer -->
    <div class="bottom-spacer"></div>

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
      <button class="nav-item" @click="$router.push('/home')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span>홈</span>
      </button>
      <button class="nav-item active" @click="$router.push('/features')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <rect x="3" y="3" width="7" height="7" rx="1.5"/>
          <rect x="14" y="3" width="7" height="7" rx="1.5"/>
          <rect x="14" y="14" width="7" height="7" rx="1.5"/>
          <rect x="3" y="14" width="7" height="7" rx="1.5"/>
        </svg>
        <span>기능</span>
      </button>
      <button class="nav-item" @click="$router.push('/history')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        <span>기록</span>
      </button>
      <button class="nav-item" @click="$router.push('/profile')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        <span>내 정보</span>
      </button>
    </nav>
  </div>
</template>

<script setup>
// FeaturesView - 반려견 스마트 케어 기능 페이지
</script>

<style scoped>
.features-page {
  min-height: 100vh;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #fafafa;
  color: #191f28;
}

/* Features Section */
.features-section {
  background: #f2f4f6;
  padding: 56px 24px;
}

.features-container {
  max-width: 980px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 36px;
}

.section-title {
  font-size: 28px;
  font-weight: 800;
  color: #191f28;
  letter-spacing: -0.02em;
  margin-bottom: 8px;
}

.section-desc {
  font-size: 15px;
  font-weight: 500;
  color: #8b95a1;
}

.features-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.features-grid:last-child {
  margin-bottom: 0;
}

@media (min-width: 768px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-bottom: 20px;
  }
}

/* Feature Card */
.feature-card {
  position: relative;
  background: #fff;
  border-radius: 20px;
  padding: 32px 28px;
  text-align: center;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid transparent;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 20px;
  padding: 1px;
  background: linear-gradient(180deg, rgba(255,255,255,0.8), rgba(255,255,255,0));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
}

.feature-card:hover::before {
  opacity: 1;
}

.feature-card:active {
  transform: translateY(-2px) scale(0.99);
}

.feature-card.dark {
  background: #191f28;
}

.feature-card.dark .card-title {
  color: #fff;
}

.feature-card.dark .card-description {
  color: #8b95a1;
}

.card-badge {
  position: absolute;
  top: 20px;
  left: 24px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  color: #fff;
  background: #ff6b6b;
  padding: 5px 10px;
  border-radius: 6px;
}

.card-badge.ai {
  background: #8b5cf6;
}

.card-badge.memo {
  background: #f59e0b;
}

.card-badge.community {
  background: #10b981;
}

.card-inner {
  position: relative;
  z-index: 1;
}

.card-title {
  font-size: 26px;
  font-weight: 700;
  color: #191f28;
  letter-spacing: -0.02em;
  margin-bottom: 10px;
  margin-top: 24px;
}

.card-description {
  font-size: 15px;
  font-weight: 500;
  color: #6b7684;
  line-height: 1.6;
  margin-bottom: 20px;
  letter-spacing: -0.01em;
}

.card-buttons {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.btn-learn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #3182f6;
  transition: all 0.2s;
}

.btn-learn:hover {
  gap: 10px;
}

.btn-learn.light {
  color: #fff;
}

.btn-learn svg {
  transition: transform 0.2s;
}

.btn-learn:hover svg {
  transform: translateX(2px);
}

.card-image-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  overflow: hidden;
}

.card-image {
  width: 100%;
  max-width: 280px;
  height: auto;
  max-height: 200px;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.feature-card:hover .card-image {
  transform: scale(1.05);
}

/* Bottom Spacer & Nav */
.bottom-spacer {
  height: 100px;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  max-width: 600px;
  margin: 0 auto;
  height: 72px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 0 8px;
  padding-bottom: env(safe-area-inset-bottom);
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
  color: #b0b8c1;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
  -webkit-tap-highlight-color: transparent;
}

.nav-item:hover {
  color: #6b7684;
}

.nav-item svg {
  width: 24px;
  height: 24px;
}

.nav-item span {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.nav-item.active {
  color: #3182f6;
}

/* Mobile Responsive */
@media (max-width: 767px) {
  .features-section {
    padding: 48px 16px;
  }

  .section-title {
    font-size: 24px;
  }

  .feature-card {
    padding: 28px 24px;
  }

  .card-title {
    font-size: 22px;
  }

  .card-description {
    font-size: 14px;
  }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  .card-image,
  .feature-card,
  .btn-learn svg {
    transition: none;
  }
}
</style>
