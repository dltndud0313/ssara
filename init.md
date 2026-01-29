# 프로젝트 실행 가이드

> 컴퓨터를 켰을 때 프로젝트를 실행하는 방법을 안내합니다.

---

## 빠른 시작 (요약)

```bash
# 1. Docker 컨테이너 실행
cd backend && docker-compose up -d

# 2. Mosquitto 실행
docker run -d --name gae_mosquitto -p 1883:1883 -p 9001:9001 -v C:/S14P11C101/mosquitto/config:/mosquitto/config -v C:/S14P11C101/mosquitto/data:/mosquitto/data -v C:/S14P11C101/mosquitto/log:/mosquitto/log eclipse-mosquitto:2

# 여기부터  도커 > 누르면 됨. 

# 3. 백엔드 실행
cd backend && ./gradlew bootRun

# 4. 프론트엔드 실행 (새 터미널)
cd frontend && npm run dev
```

---

## 상세 실행 가이드

### 1단계: Docker Desktop 실행

1. **Docker Desktop** 앱을 실행합니다
2. Docker가 완전히 시작될 때까지 대기합니다 (트레이 아이콘이 녹색으로 변경)

---

### 2단계: PostgreSQL 데이터베이스 실행

```bash
cd C:/S14P11C101/backend
docker-compose up -d
```

**확인 방법:**
```bash
docker ps
```

**정상 출력:**
```
CONTAINER ID   IMAGE               STATUS          PORTS                    NAMES
xxxxxxxx       postgres:15-alpine   Up X seconds   0.0.0.0:5432->5432/tcp   gae_postgres
```

---

### 3단계: MQTT 브로커 (Mosquitto) 실행

**이미 실행 중인 경우:**
```bash
docker start gae_mosquitto
```

**처음 실행하는 경우:**
```bash
docker run -d --name gae_mosquitto ^
  -p 1883:1883 ^
  -p 9001:9001 ^
  -v C:/S14P11C101/mosquitto/config:/mosquitto/config ^
  -v C:/S14P11C101/mosquitto/data:/mosquitto/data ^
  -v C:/S14P11C101/mosquitto/log:/mosquitto/log ^
  eclipse-mosquitto:2
```

**확인 방법:**
```bash
docker ps
```

**정상 출력:**
```
CONTAINER ID   IMAGE                 STATUS          PORTS                                       NAMES
xxxxxxxx       eclipse-mosquitto:2   Up X seconds   0.0.0.0:1883->1883/tcp, 0.0.0.0:9001->9001   gae_mosquitto
```

---

### 4단계: 백엔드 서버 실행

```bash
cd C:/S14P11C101/backend
./gradlew bootRun
```

**정상 실행 확인:**
```
Started GaeServerApplication in X.XXX seconds
```

**접속 확인:**
- http://localhost:8080 접속 시 `401 Unauthorized` 응답이 나오면 정상

---

### 5단계: 프론트엔드 실행

**새 터미널을 열고:**
```bash
cd C:/S14P11C101/frontend
npm run dev
```

**정상 실행 확인:**
```
VITE v7.x.x ready

➜  Local:   http://localhost:5173/
```

**접속:**
- 브라우저에서 http://localhost:5173 접속

---

## 전체 실행 상태 확인

### Docker 컨테이너 상태
```bash
docker ps
```

| 컨테이너 | 이미지 | 포트 | 용도 |
|---------|--------|------|------|
| gae_postgres | postgres:15-alpine | 5432 | 데이터베이스 |
| gae_mosquitto | eclipse-mosquitto:2 | 1883, 9001 | MQTT 브로커 |

### 서비스 포트

| 서비스 | URL | 설명 |
|--------|-----|------|
| 프론트엔드 | http://localhost:5173 | Vue.js 개발 서버 |
| 백엔드 API | http://localhost:8080 | Spring Boot |
| PostgreSQL | localhost:5432 | 데이터베이스 |
| MQTT | localhost:1883 | MQTT 브로커 |
| MQTT WebSocket | localhost:9001 | MQTT WebSocket |

---

## 종료 방법

### 1. 프론트엔드 종료
- 터미널에서 `Ctrl + C`

### 2. 백엔드 종료
- 터미널에서 `Ctrl + C`

### 3. Docker 컨테이너 종료
```bash
# 개별 종료
docker stop gae_postgres gae_mosquitto

# 또는 docker-compose로 종료
cd backend && docker-compose down
```

---

## 문제 해결

### 포트가 이미 사용 중인 경우

**Windows에서 포트 사용 프로세스 확인:**
```bash
netstat -ano | findstr :8080
netstat -ano | findstr :5432
netstat -ano | findstr :5173
```

**프로세스 종료:**
```bash
taskkill /PID <PID번호> /F
```

---

### Docker 컨테이너가 시작되지 않는 경우

```bash
# 기존 컨테이너 삭제 후 재생성
docker rm -f gae_postgres gae_mosquitto

# docker-compose로 재시작
cd backend && docker-compose up -d

# Mosquitto 재생성
docker run -d --name gae_mosquitto -p 1883:1883 -p 9001:9001 eclipse-mosquitto:2
```

---

### 백엔드가 DB 연결에 실패하는 경우

1. PostgreSQL 컨테이너 실행 확인:
```bash
docker ps | findstr postgres
```

2. DB 비밀번호 확인 (`backend/src/main/resources/application-dev.yml`):
```yaml
datasource:
  url: jdbc:postgresql://localhost:5432/dog_gaje_db
  username: postgres
  password: your_password  # docker-compose.yml과 동일해야 함
```

---

### 프론트엔드 의존성 오류

```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

---

## 개발 환경 설정 (최초 1회)

### 환경 변수 파일 생성

**백엔드:**
```bash
cd backend
cp .env.example .env
# .env 파일을 열어 실제 값으로 수정
```

**프론트엔드:**
```bash
cd frontend
cp .env.example .env
# .env 파일을 열어 실제 값으로 수정
```

---

## 실행 순서 체크리스트

| 순서 | 작업 | 명령어 | 확인 |
|------|------|--------|------|
| 1 | Docker Desktop 실행 | (앱 실행) | |
| 2 | PostgreSQL 실행 | `docker-compose up -d` | |
| 3 | Mosquitto 실행 | `docker start gae_mosquitto` | |
| 4 | 백엔드 실행 | `./gradlew bootRun` | |
| 5 | 프론트엔드 실행 | `npm run dev` | |
| 6 | 브라우저 접속 | http://localhost:5173 | |

---

*작성일: 2026-01-29*
