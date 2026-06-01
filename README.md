# GAE

> AIoT 기반 반려견 돌봄 로봇 서비스

GAE는 보호자가 모바일 웹에서 반려견 돌봄 로봇의 상태를 확인하고, 실시간 영상/위치/활동 로그를 모니터링하며, 로봇 이동 명령을 보낼 수 있는 AIoT 서비스입니다.  
Vue 프론트엔드, Spring Boot 백엔드, MQTT/WebSocket 통신, ROS2 로봇 환경을 연결해 로봇 제어와 관제 흐름을 하나의 서비스로 구성했습니다.

## 담당 파트

제가 주로 담당한 영역은 `gae_ws/src/gae_perception`의 **로봇 인식(Perception) 파이프라인**입니다.

| 담당 영역 | 구현 내용 |
| --- | --- |
| RGB-D 카메라 처리 | Orbbec Astra Pro의 RGB/Depth 토픽 구독 및 OpenCV 변환 |
| 객체 인식 | YOLO 기반 객체 탐지 노드 구현 |
| 거리 추정 | Depth 이미지에서 객체 중심 주변 유효 픽셀을 사용해 거리 계산 |
| 주행 판단 | 장애물/신호등 인식 결과를 기반으로 `/cmd_vel` 제어 판단 |
| SLAM 연동 | RTAB-Map 위치 정보를 MQTT `robot/pose` 토픽으로 전송 |
| 웹 연동 | Depth 이미지를 웹 표시용 8-bit 이미지로 변환 |
| 데이터 수집 | 학습 데이터 확보를 위한 ROS Image 녹화 노드 구현 |
| Launch 구성 | 카메라, SLAM, 추론, 웹 영상 서버, MQTT bridge 실행 흐름 구성 |

### Perception 패키지 구조

```text
gae_ws/src/gae_perception/
├─ gae_perception/
│  ├─ inference_node.py   # YOLO 객체 탐지 + Depth 기반 거리 추정
│  ├─ decision_node.py    # 장애물/신호등 기반 주행 판단
│  ├─ depth_to_web.py     # Depth 영상을 웹 표시용 이미지로 변환
│  ├─ pose_bridge.py      # SLAM pose를 MQTT robot/pose로 publish
│  └─ data_recorder.py    # 카메라 토픽을 mp4로 저장해 데이터셋 수집
├─ launch/
│  ├─ slam.launch.py
│  └─ record_dataset.launch.py
├─ config/maps/           # RTAB-Map 기반 2D/3D map 산출물
└─ weights/               # YOLO/TensorRT 모델 배치 위치
```

### Perception 데이터 흐름

```text
Orbbec Astra Pro
  |  /camera/color/image_raw
  |  /camera/depth/image_raw
  v
inference_node.py
  |  /gae_perception/yolo_result
  |  /gae_perception/yolo_image
  v
decision_node.py
  |  /cmd_vel
  v
Robot Control

RTAB-Map SLAM
  |  /rtabmap/localization_pose
  v
pose_bridge.py
  |  MQTT robot/pose
  v
Backend / Frontend
```

### 구현 포인트

- `message_filters.ApproximateTimeSynchronizer`로 RGB 이미지와 Depth 이미지를 동기화해 객체 인식 결과와 거리 정보를 함께 계산했습니다.
- 객체 bounding box 중심 주변 Depth ROI에서 0이 아닌 유효 픽셀만 추출하고, 평균 대신 median을 사용해 노이즈에 강한 거리값을 만들었습니다.
- TensorRT engine 파일이 있으면 우선 사용하고, 없으면 기본 YOLO 모델로 fallback하도록 구성했습니다.
- 프레임 스킵을 적용해 Jetson 환경에서 추론 부하를 줄였습니다.
- SLAM pose는 MQTT로 직접 publish해 백엔드/프론트엔드의 실시간 위치 표시 흐름과 연결했습니다.
- Depth 원본을 브라우저에서 보기 쉬운 8-bit mono 이미지로 변환해 웹 영상 서버와 함께 확인할 수 있게 했습니다.

## 프로젝트 개요

| 항목 | 내용 |
| --- | --- |
| 프로젝트명 | GAE |
| 주제 | 반려견 돌봄 로봇 관제 및 제어 플랫폼 |
| 형태 | 모바일 웹 + 백엔드 API + 로봇/IoT 통신 |
| 주요 사용자 | 외출 중인 반려견 보호자 |
| 핵심 가치 | 실시간 상태 확인, 원격 제어, 이상 상황 기록, AI 비서 연동 |

## 주요 기능

### 사용자 및 인증

- 회원가입, 로그인, JWT 기반 인증
- 이메일 찾기, 비밀번호 재설정, 임시 비밀번호 발급
- Axios 인터셉터를 통한 인증 토큰 자동 첨부 및 401 응답 처리

### 로봇 관제

- 로봇 배터리, 온라인 상태, 위치 정보 조회
- MQTT로 수신한 로봇 상태를 WebSocket(STOMP)으로 프론트엔드에 실시간 전달
- VSLAM 좌표를 GPS 좌표로 변환해 지도 기반 위치 표시

### 로봇 제어

- 전진/후진/회전 속도 제어
- 정지, 홈 복귀, 목표 좌표 이동 명령
- 백엔드에서 Rosbridge Protocol 형식의 `/cmd_vel` 메시지를 생성해 MQTT로 발행

### 활동 기록 및 알림

- 로봇 활동 로그 저장 및 날짜별 조회
- 오늘/어제 활동 기록, 일일 요약 정보 조회
- 이상 감지 이벤트를 활동 로그로 저장
- Firebase Cloud Messaging 기반 알림 토큰 등록 및 알림 설정 관리

### AI 비서 및 외부 API

- GMS API 프록시를 통한 AI 채팅 기능
- Kakao API 기반 좌표-주소 변환 및 주변 장소 검색
- 보호자 관점의 질문/요청을 처리하는 AI 비서 화면 구성

## 시스템 아키텍처

```text
Robot / ROS2
  |  publish: robot/status, robot/pose, robot/activity, robot/summary
  v
Mosquitto MQTT Broker
  |
  v
Spring Boot Backend
  |  - MQTT subscribe / publish
  |  - JWT 인증
  |  - PostgreSQL 저장
  |  - STOMP WebSocket broadcast
  v
Vue Frontend
  |  - 모바일 웹 UI
  |  - 실시간 로봇 상태 표시
  |  - 로봇 제어 명령 요청
  |  - 활동 기록/AI 비서/지도 화면
```

## 기술 스택

### Frontend

| 기술 | 사용 목적 |
| --- | --- |
| Vue 3 | 모바일 웹 화면 구성 |
| Vite | 개발 서버 및 번들링 |
| Pinia | 로봇 상태, 활동 기록, AI 채팅 상태 관리 |
| Vue Router | 인증 기반 페이지 라우팅 |
| Axios | REST API 통신 |
| STOMP WebSocket | 로봇 상태 실시간 수신 |
| Firebase | FCM 알림 연동 |
| Kakao Map API | 지도, 위치 검색, 좌표 변환 |

### Backend

| 기술 | 사용 목적 |
| --- | --- |
| Java 17 | 백엔드 개발 언어 |
| Spring Boot 4 | REST API 서버 |
| Spring Security | JWT 기반 인증/인가 |
| Spring Data JPA | 도메인 모델 및 DB 접근 |
| PostgreSQL | 회원, 로봇, 활동 로그 저장 |
| Spring Integration MQTT | MQTT 수신/발행 |
| WebSocket(STOMP) | 실시간 데이터 브로드캐스트 |
| Firebase Admin SDK | FCM 알림 처리 |
| Gradle | 빌드 및 의존성 관리 |

### Robot / IoT

| 기술 | 사용 목적 |
| --- | --- |
| ROS2 Humble | 로봇 노드 구성 |
| Mosquitto | MQTT Broker |
| Rosbridge Protocol | 로봇 속도 명령 메시지 포맷 |
| NVIDIA Jetson | 로봇 엣지 컴퓨팅 환경 |
| RTAB-Map / VSLAM | 위치 추정 및 지도 기반 이동 |

## 핵심 구현 포인트

### 1. MQTT와 WebSocket을 연결한 실시간 관제 흐름

로봇은 MQTT 토픽으로 상태와 위치를 발행하고, 백엔드는 이를 구독한 뒤 프론트엔드 WebSocket 토픽으로 다시 브로드캐스트합니다.  
이 구조를 통해 프론트엔드는 MQTT 브로커와 직접 강하게 결합되지 않고도 로봇 상태를 실시간으로 받을 수 있습니다.

```text
robot/status   -> /topic/robot/status
robot/pose     -> /topic/robot/pose
robot/activity -> /topic/robot/activity
robot/summary  -> /topic/robot/summary
```

### 2. REST API 기반 로봇 명령 추상화

프론트엔드는 `/api/robot/control`, `/api/robot/nav`, `/api/robot/home` 같은 REST API만 호출합니다.  
백엔드는 요청을 검증한 뒤 MQTT 명령 토픽으로 변환해 로봇에 전달합니다.

```json
{
  "op": "publish",
  "topic": "/cmd_vel",
  "msg": {
    "linear": { "x": 0.5, "y": 0.0, "z": 0.0 },
    "angular": { "x": 0.0, "y": 0.0, "z": 0.3 }
  }
}
```

### 3. JWT 기반 보호자 인증

로그인 성공 시 JWT를 발급하고, 보호된 API 요청에는 `Authorization: Bearer <token>` 헤더를 사용합니다.  
백엔드는 Spring Security 필터 체인에서 JWT를 검증하고, 프론트엔드는 라우터 가드로 인증이 필요한 화면 접근을 제어합니다.

### 4. 활동 로그 저장과 조회

로봇에서 발생한 이상 감지 이벤트를 MQTT로 수신하면 백엔드가 활동 로그로 저장합니다.  
이후 보호자는 오늘/어제/특정 날짜 기준으로 활동 기록과 일일 요약을 조회할 수 있습니다.

## API 요약

| 구분 | Method | Endpoint | 설명 |
| --- | --- | --- | --- |
| Auth | POST | `/api/auth/signup` | 회원가입 |
| Auth | POST | `/api/auth/login` | 로그인 및 JWT 발급 |
| Auth | POST | `/api/auth/find-email` | 이메일 찾기 |
| Auth | POST | `/api/auth/reset-password` | 비밀번호 재설정 |
| Member | GET | `/api/members/me` | 내 정보 조회 |
| Member | PATCH | `/api/members/me` | 내 정보 수정 |
| Robot | GET | `/api/robots/me` | 내 로봇 조회 |
| Robot | PATCH | `/api/robots/me` | 로봇 정보 수정 |
| Robot | POST | `/api/robot/control` | 속도 제어 |
| Robot | POST | `/api/robot/home` | 홈 복귀 |
| Robot | POST | `/api/robot/nav` | 목표 좌표 이동 |
| Activity | GET | `/api/activities/today` | 오늘 활동 로그 |
| Activity | GET | `/api/activities/yesterday` | 어제 활동 로그 |
| Activity | GET | `/api/activities/date/{date}` | 날짜별 활동 로그 |
| Activity | GET | `/api/activities/summary/today` | 오늘 요약 |
| Notification | POST | `/api/notifications/token` | FCM 토큰 등록 |
| Notification | PATCH | `/api/notifications/settings` | 알림 설정 변경 |
| Proxy | POST | `/api/proxy/gms/chat` | AI 채팅 프록시 |
| Proxy | GET | `/api/proxy/kakao/search` | Kakao 장소 검색 |

## MQTT 토픽

### Subscribe: Robot -> Backend

| Topic | 설명 |
| --- | --- |
| `robot/status` | 배터리, 온라인 상태 |
| `robot/pose` | VSLAM 기반 로봇 위치 |
| `robot/map` | 지도 데이터 |
| `robot/activity` | 이상 감지 및 활동 이벤트 |
| `robot/summary` | 일일 요약 정보 |

### Publish: Backend -> Robot

| Topic | 설명 |
| --- | --- |
| `robot/cmd/vel` | Rosbridge 형식 속도 명령 |
| `robot/cmd/move` | 홈 복귀, 정지 명령 |
| `robot/cmd/nav` | 목표 좌표 이동 명령 |

## 폴더 구조

```text
S14P11C101/
├─ backend/       # Spring Boot API 서버
├─ frontend/      # Vue 모바일 웹
├─ gae_ws/        # ROS2 로봇 워크스페이스
├─ dummies_ros2/  # 로봇/브릿지 테스트용 더미 노드
├─ mosquitto/     # MQTT 브로커 설정
├─ rl_ws/         # 로봇 학습/시뮬레이션 관련 자료
├─ aiot_GAE/      # AIoT 실험 및 모델 자료
├─ docs/          # 문서
└─ exec/          # 포팅/배포 문서
```

## 실행 방법

### Backend

```bash
cd backend
docker-compose up -d
./gradlew bootRun
```

기본 서버 주소:

```text
http://localhost:8080
```

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

기본 개발 서버 주소:

```text
http://localhost:5173
```

### Mosquitto

```bash
mosquitto -c mosquitto/config/mosquitto.conf
```

또는 Docker 환경에서 MQTT broker를 실행해 로봇, 백엔드, 프론트엔드 간 메시지를 중계합니다.

## 환경 변수

실행 전 아래 설정 파일을 준비해야 합니다.

| 위치 | 용도 |
| --- | --- |
| `backend/.env` | DB 접속 정보, JWT Secret, Firebase 설정 |
| `frontend/.env` | API URL, Firebase, Kakao, GMS API Key |
| `mosquitto/config/mosquitto.conf` | MQTT broker 포트 및 인증 설정 |

보안 정보가 포함된 실제 `.env` 파일과 Firebase 서비스 계정 키는 Git에 포함하지 않습니다.

## 포트폴리오 관점의 성과

- RGB-D 카메라, YOLO, Depth 거리 추정, SLAM pose 전송을 하나의 ROS2 perception 패키지로 구성
- 로봇 인식 결과를 `/gae_perception/yolo_result`, `/gae_perception/yolo_image`, MQTT `robot/pose` 등 후속 시스템이 사용할 수 있는 토픽으로 정리
- Jetson 환경의 성능 제약을 고려해 TensorRT 모델 경로, frame skip, 이미지 해상도 설정을 적용
- 인식 결과가 단순 화면 표시에서 끝나지 않고 주행 판단(`/cmd_vel`)과 웹 관제 위치 표시까지 이어지도록 연결
- 전체 서비스에서는 REST API, MQTT, WebSocket, ROS2가 이어지는 AIoT 로봇 서비스 구조를 경험

## 트러블슈팅

### Windows에서 긴 경로 파일이 삭제된 것처럼 보이는 경우

로봇/SDK 레퍼런스 파일 중 경로가 긴 파일이 있어 Windows Git에서 `Filename too long` 문제가 발생할 수 있습니다.

```bash
git config core.longpaths true
git restore .
git status
```

필요하면 전역 설정으로 적용합니다.

```bash
git config --global core.longpaths true
```
