# 커밋 전 변경사항 정리

## 개요
MQTT 실시간 데이터 연동 강화 및 프론트엔드 UI 개선

---

## Backend 변경사항

### 1. MqttService.java
**경로:** `backend/src/main/java/com/gae/server/api/mqtt/MqttService.java`

- **MQTT 토픽 추가 처리**
  - `robot/activity`: 이상 감지 이벤트 수신 및 DB 저장
  - `robot/summary`: 일일 요약 데이터 WebSocket 브로드캐스트

- **DB 연동 기능 추가**
  - `updateRobotStatus()`: 배터리, 온라인 상태를 Robot 테이블에 저장
  - `updateRobotPose()`: 로봇 위치 정보를 Robot 테이블에 저장
  - `saveActivityLog()`: 활동 로그를 ActivityLog 테이블에 저장

- **의존성 추가**
  - `RobotRepository`, `ActivityLogRepository` 주입

### 2. MqttConfig.java
**경로:** `backend/src/main/java/com/gae/server/global/config/MqttConfig.java`

- **구독 토픽 추가**
  - `robot/activity`
  - `robot/summary`

### 3. application-dev.yml.example
**경로:** `backend/src/main/resources/application-dev.yml.example`

- SMTP 설정 예시 업데이트

---

## Frontend 변경사항

### 1. robotStore.js
**경로:** `frontend/src/stores/robotStore.js`

- **State 추가**
  - `dailySummary`: 일일 요약 (산책시간, 이상감지, 이동거리, 총 이벤트)
  - `activityLogs`: 최근 활동 로그 (최대 10개)

- **WebSocket 구독 추가**
  - `/topic/robot/summary`: 일일 요약 실시간 수신
  - `/topic/robot/activity`: 이상 감지 이벤트 실시간 수신

### 2. HomeView.vue
**경로:** `frontend/src/views/HomeView.vue`

- **실시간 데이터 연동**
  - API 초기 데이터 + WebSocket 실시간 데이터 병합
  - `todaySummary`: computed로 실시간 요약 표시
  - `displayLogs`: WebSocket 로그 우선, DB 로그 병합하여 표시

- **UI/CSS 개선**
  - `.content`: `overflow-x: hidden` 추가 (자식 요소 overflow 방지)
  - `.status-card`: `max-width: 100%`, `overflow: hidden`, `box-sizing: border-box`, `margin-top: 12px`로 조정
  - `.robot-info`: `min-width: 0`, `overflow: hidden` 추가
  - `.robot-name`: 긴 텍스트 말줄임 처리 (`text-overflow: ellipsis`)

### 3. HistoryView.vue
**경로:** `frontend/src/views/HistoryView.vue`

- **실시간 데이터 연동**
  - `robotStore` 연결하여 오늘 날짜일 경우 WebSocket 실시간 데이터 표시
  - 과거 날짜는 API 로그 기반 계산

- **UI 개선**
  - 이동 거리 통계 항목 제거 (불필요)

- **WebSocket 관리**
  - `onMounted`에서 연결, `onUnmounted`에서 해제
  - `watch`로 실시간 요약 데이터 변경 감지

---

## 삭제된 파일
- `SMTP.md`
- `project_outline.md`

---

## 요약
| 구분 | 파일 수 | 추가 | 삭제 |
|------|---------|------|------|
| Backend | 3 | ~108 lines | ~1 line |
| Frontend | 3 | ~144 lines | ~35 lines |
| **총합** | **6** | **~252 lines** | **~356 lines** |
