<template>
  <div class="profile">
    <header class="header">
      <button class="back-btn" @click="$router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="header-title">내 정보</h1>
      <div style="width: 24px;"></div>
    </header>

    <main class="content">
      <!-- 프로필 카드 -->
      <section class="profile-card">
        <div class="avatar">{{ userInfo.name?.charAt(0) || '?' }}</div>
        <div class="user-info">
          <h2 class="user-name">{{ userInfo.name }}</h2>
          <p class="user-email">{{ userInfo.email }}</p>
        </div>
      </section>

      <!-- 정보 섹션 -->
      <section class="section">
        <h3 class="section-title">기본 정보</h3>
        <div class="info-card">
          <div class="info-item">
            <span class="label">이름</span>
            <input
              v-if="isEditing"
              type="text"
              v-model="editForm.name"
              class="edit-input"
            />
            <span v-else class="value">{{ userInfo.name }}</span>
          </div>
          <div class="info-item">
            <span class="label">이메일</span>
            <span class="value text-tertiary">{{ userInfo.email }}</span>
          </div>
          <div class="info-item">
            <span class="label">전화번호</span>
            <input
              v-if="isEditing"
              type="tel"
              v-model="editForm.phoneNumber"
              placeholder="입력해 주세요"
              class="edit-input"
            />
            <span v-else class="value">{{ userInfo.phoneNumber || '미등록' }}</span>
          </div>
          <div v-if="isEditing" class="info-item">
            <span class="label">새 비밀번호</span>
            <input
              type="password"
              v-model="editForm.password"
              placeholder="변경 시에만 입력"
              class="edit-input"
            />
          </div>
        </div>

        <div class="button-row">
          <template v-if="isEditing">
            <button class="btn btn-secondary" @click="cancelEdit">취소</button>
            <button class="btn btn-primary" @click="saveChanges" :disabled="saving">
              {{ saving ? '저장 중...' : '저장' }}
            </button>
          </template>
          <button v-else class="btn btn-secondary full" @click="isEditing = true">
            정보 수정
          </button>
        </div>
      </section>

      <!-- 연결된 로봇 -->
      <section class="section">
        <h3 class="section-title">연결된 로봇</h3>
        <div class="robot-card">
          <div class="robot-avatar">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/>
              <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
              <line x1="9" y1="9" x2="9.01" y2="9"/>
              <line x1="15" y1="9" x2="15.01" y2="9"/>
            </svg>
          </div>
          <div class="robot-info">
            <span class="robot-name">{{ robotState.name }}</span>
            <span class="robot-status" :class="{ online: robotState.status === 'ONLINE' }">
              {{ robotState.status === 'ONLINE' ? '연결됨' : '오프라인' }}
            </span>
          </div>
          <div class="robot-battery">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="1" y="6" width="18" height="12" rx="2" ry="2"/>
              <line x1="23" y1="13" x2="23" y2="11"/>
            </svg>
            {{ robotState.battery }}%
          </div>
        </div>
      </section>

      <!-- 계정 관리 -->
      <section class="section">
        <h3 class="section-title">계정</h3>
        <div class="menu-list">
          <button class="menu-item" @click="handleLogout">
            <span>로그아웃</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
          </button>
          <button class="menu-item danger" @click="handleDelete">
            <span>회원 탈퇴</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
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
      <button class="nav-item active">
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
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { memberApi } from '../api';
import { robotState } from '../store.js';

const router = useRouter();

const userInfo = reactive({
  name: '',
  email: '',
  phoneNumber: ''
});

const editForm = reactive({
  name: '',
  phoneNumber: '',
  password: ''
});

const isEditing = ref(false);
const saving = ref(false);

const fetchMyInfo = async () => {
  try {
    const response = await memberApi.getMyInfo();
    Object.assign(userInfo, response.data);
    editForm.name = userInfo.name;
    editForm.phoneNumber = userInfo.phoneNumber || '';
  } catch (error) {
    console.error('정보 조회 실패:', error);
  }
};

const cancelEdit = () => {
  isEditing.value = false;
  editForm.name = userInfo.name;
  editForm.phoneNumber = userInfo.phoneNumber || '';
  editForm.password = '';
};

const saveChanges = async () => {
  if (!editForm.name.trim()) {
    alert('이름을 입력해 주세요');
    return;
  }

  saving.value = true;
  try {
    await memberApi.updateMyInfo({
      name: editForm.name,
      phoneNumber: editForm.phoneNumber || null,
      password: editForm.password || null
    });
    alert('정보가 수정되었어요');
    isEditing.value = false;
    editForm.password = '';
    await fetchMyInfo();
  } catch (error) {
    console.error('수정 실패:', error);
    alert('수정에 실패했어요');
  } finally {
    saving.value = false;
  }
};

const handleLogout = () => {
  if (confirm('로그아웃 하시겠어요?')) {
    localStorage.removeItem('accessToken');
    router.push('/');
  }
};

const handleDelete = async () => {
  if (!confirm('정말 탈퇴하시겠어요?')) return;
  if (!confirm('탈퇴하면 모든 데이터가 삭제되고 복구할 수 없어요. 계속할까요?')) return;

  try {
    await memberApi.deleteAccount();
    alert('탈퇴가 완료되었어요');
    localStorage.removeItem('accessToken');
    router.push('/');
  } catch (error) {
    console.error('탈퇴 실패:', error);
    alert('탈퇴에 실패했어요');
  }
};

onMounted(() => {
  fetchMyInfo();
});
</script>

<style scoped>
.profile {
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
  position: sticky;
  top: 0;
  z-index: 10;
}

.back-btn {
  padding: 8px;
  color: var(--text-primary);
}

.header-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
}

.content {
  padding: 20px;
}

/* 프로필 카드 */
.profile-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--bg-primary);
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 24px;
}

.avatar {
  width: 56px;
  height: 56px;
  background: var(--primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.user-email {
  font-size: 14px;
  color: var(--text-tertiary);
}

/* 섹션 */
.section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 10px;
  padding-left: 4px;
}

.info-card {
  background: var(--bg-primary);
  border-radius: 16px;
  overflow: hidden;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  border-bottom: 1px solid var(--gray-100);
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  font-size: 14px;
  color: var(--text-secondary);
}

.info-item .value {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.info-item .value.text-tertiary {
  color: var(--text-tertiary);
}

.edit-input {
  text-align: right;
  width: 180px;
  height: 36px;
  padding: 0 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-primary);
}

.edit-input:focus {
  border-color: var(--primary);
  background: var(--bg-primary);
}

/* 버튼 */
.button-row {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

.btn {
  flex: 1;
  height: 48px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  transition: opacity 0.2s;
}

.btn.full {
  flex: none;
  width: 100%;
}

.btn-primary {
  background: var(--primary);
  color: white;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.btn:disabled {
  opacity: 0.6;
}

.btn:not(:disabled):active {
  opacity: 0.9;
}

/* 로봇 카드 */
.robot-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--bg-primary);
  padding: 16px 18px;
  border-radius: 16px;
}

.robot-avatar {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, var(--primary) 0%, #5BA0F5 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.robot-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.robot-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.robot-status {
  font-size: 13px;
  color: var(--text-tertiary);
}

.robot-status.online {
  color: var(--success);
}

.robot-battery {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
}

/* 메뉴 */
.menu-list {
  background: var(--bg-primary);
  border-radius: 16px;
  overflow: hidden;
}

.menu-item {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  font-size: 15px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--gray-100);
  transition: background 0.2s;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:active {
  background: var(--gray-50);
}

.menu-item.danger {
  color: var(--danger);
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
