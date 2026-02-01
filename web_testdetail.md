# MQTT 개별 기능 테스트 가이드

> 각 기능별로 독립적으로 테스트할 수 있는 상세 가이드
>
> **테스트 계정**: test@test.com / test1234
> **로봇 S/N**: TEST-ROBOT-001

---

## 사전 준비

### 1. 필수 서비스 실행 확인

| 서비스 | 포트 | 확인 방법 |
|--------|------|-----------|
| Mosquitto MQTT | 1883 | `netstat -an \| findstr 1883` |
| Spring Boot | 8080 | http://localhost:8080 (401 응답이면 정상) |
| Frontend | 5173 | http://localhost:5173 |

### 2. 패키지 설치

```bash
pip install paho-mqtt
```

### 3. 테스트 스크립트 위치

```
C:\S14P11C101\mqtt_test.py  # 통합 테스트 스크립트
```

### 4. 웹 로그인

1. http://localhost:5173 접속
2. **test@test.com** / **test1234** 로 로그인
3. 홈 화면에서 데이터 확인

---

## 테스트 1: 배터리 변경 (100 → 80)

### 1.1 목적
MQTT로 배터리 상태를 전송하면 웹에서 실시간으로 반영되는지 확인

### 1.2 데이터 흐름
```
Python Script → MQTT (1883) → Spring Boot → DB 저장 + WebSocket → Frontend
```

### 1.3 통합 스크립트 사용

```bash
python mqtt_test.py 1
```

**출력 예시:**
```
==================================================
MQTT 테스트 스크립트
==================================================

MQTT 브로커 연결 중...
연결 성공!

[테스트 1] 배터리 80%로 변경...
  -> robot/status 전송 완료: {'battery': 80, 'state': 'IDLE', 'isOnline': True}

테스트 완료!
웹에서 확인하세요: http://localhost:5173/home
```

### 1.4 개별 Python 스크립트

파일: `test_battery.py`

```python
#!/usr/bin/env python3
"""배터리 변경 테스트"""
import paho.mqtt.client as mqtt
import json
import time

def get_client():
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        client = mqtt.Client()
    client.connect('localhost', 1883, 60)
    client.loop_start()
    return client

client = get_client()

print("=== 배터리 테스트 ===\n")

# 배터리 100%
print("[1] 배터리 100% 전송")
status = {'battery': 100, 'state': 'IDLE', 'isOnline': True}
info = client.publish('robot/status', json.dumps(status))
info.wait_for_publish()
print("    → 웹에서 배터리 100% 확인")
print("    → http://localhost:5173/home")

input("\n[Enter] 를 눌러 80%로 변경...")

# 배터리 80%
print("[2] 배터리 80% 전송")
status = {'battery': 80, 'state': 'IDLE', 'isOnline': True}
info = client.publish('robot/status', json.dumps(status))
info.wait_for_publish()
print("    → 웹에서 배터리 80% 확인")

time.sleep(0.5)
client.loop_stop()
client.disconnect()
print("\n테스트 완료!")
```

### 1.5 확인 항목

| 단계 | 웹 화면 위치 | 예상 값 | 색상 |
|------|-------------|---------|------|
| 초기 | 홈 > 배터리 | 100% | 녹색 |
| 변경 후 | 홈 > 배터리 | 80% | 녹색 |
| 30% 테스트 | 홈 > 배터리 | 30% | 노란색 |
| 10% 테스트 | 홈 > 배터리 | 10% | 빨간색 |

### 1.6 DB 저장 확인

```bash
# API로 확인
curl -s http://localhost:8080/api/robots/me -H "Authorization: Bearer <토큰>"
# 응답: {"battery": 80, "status": "ONLINE", ...}
```

---

## 테스트 2: 산책시간, 알림, 이상감지

### 2.1 목적
YOLO에서 보내는 일일 요약(산책시간, 이상감지)과 활동 이벤트가 웹에 표시되는지 확인

### 2.2 데이터 종류

| 토픽 | 용도 | 저장 위치 |
|------|------|-----------|
| robot/summary | 일일 요약 | WebSocket 실시간만 |
| robot/activity | 활동 이벤트 | DB 저장 (activity_logs) |

### 2.3 통합 스크립트 사용

```bash
python mqtt_test.py 2   # 산책시간/알림만
python mqtt_test.py 3   # 낙상 감지 이벤트만
```

### 2.4 개별 Python 스크립트

파일: `test_summary.py`

```python
#!/usr/bin/env python3
"""산책시간/알림/이상감지 테스트"""
import paho.mqtt.client as mqtt
import json
import time

def get_client():
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        client = mqtt.Client()
    client.connect('localhost', 1883, 60)
    client.loop_start()
    return client

client = get_client()

print("=== 산책시간/알림/이상감지 테스트 ===\n")

# 일일 요약 전송
print("[1] 일일 요약 전송")
summary = {
    'walkTime': 75,      # 산책 75분
    'alerts': 4,         # 이상감지 4건
    'distance': 3.5,     # 3.5km
    'totalEvents': 25    # 총 25건
}
info = client.publish('robot/summary', json.dumps(summary))
info.wait_for_publish()
print(f"    산책시간: {summary['walkTime']}분")
print(f"    이상감지: {summary['alerts']}건")
print(f"    총 이벤트: {summary['totalEvents']}건")
print("\n    → 홈 화면 '오늘 하루' 확인")

input("\n[Enter] 를 눌러 이상감지 이벤트 전송...")

# 이상감지 이벤트 (DB에 저장됨)
print("[2] 이상감지 이벤트 전송 (DB 저장)")
events = [
    {'type': 'ALERT', 'message': '낙상 감지!', 'severity': 'HIGH'},
    {'type': 'ALERT', 'message': '비정상 움직임', 'severity': 'HIGH'},
    {'type': 'INFO', 'message': '산책 완료', 'severity': 'LOW'},
]

for event in events:
    info = client.publish('robot/activity', json.dumps(event))
    info.wait_for_publish()
    icon = "[경고]" if event['severity'] == 'HIGH' else "[정보]"
    print(f"    {icon} {event['message']}")
    time.sleep(0.3)

print("\n    → 홈 화면 '최근 활동' 확인")
print("    → 기록 화면 활동 로그 확인")

time.sleep(0.5)
client.loop_stop()
client.disconnect()
print("\n테스트 완료!")
```

### 2.5 확인 항목

| 화면 | 위치 | 데이터 소스 | 예상 값 |
|------|------|------------|---------|
| 홈 | 오늘 하루 > 산책 시간 | API (DB) | 계산값 |
| 홈 | 오늘 하루 > 이상 감지 | API (DB) | WARNING 개수 |
| 홈 | 최근 활동 | API + WebSocket | 낙상 감지! 등 |
| 기록 | 활동 로그 | API (DB) | 전체 이벤트 목록 |

### 2.6 DB 저장 확인

```bash
# 오늘 활동 로그 조회
curl -s "http://localhost:8080/api/activities/today" -H "Authorization: Bearer <토큰>"

# 오늘 요약 조회
curl -s "http://localhost:8080/api/activities/summary/today" -H "Authorization: Bearer <토큰>"
```

---

## 테스트 3: 집으로 복귀 명령

### 3.1 목적
웹에서 '집으로 복귀' 버튼을 누르면 로봇이 명령을 수신하는지 확인

### 3.2 사전 조건

**MQTT 시뮬레이터 실행 필요:**
```bash
python C:/S14P11C101/ros2_ws/src/mqtt_robot_simulator.py
```

### 3.3 테스트 방법

**방법 1: 웹 UI에서 테스트**
1. http://localhost:5173/location 접속
2. '집으로' 버튼 클릭
3. 시뮬레이터 터미널에서 `[명령] 집으로 이동!` 확인

**방법 2: MQTT 직접 전송**
```bash
python mqtt_test.py 3   # 참고: mqtt_test.py에는 없음, 아래 스크립트 사용
```

### 3.4 개별 Python 스크립트

파일: `test_go_home.py`

```python
#!/usr/bin/env python3
"""집으로 복귀 명령 테스트"""
import paho.mqtt.client as mqtt
import json
import time

def get_client():
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        client = mqtt.Client()
    client.connect('localhost', 1883, 60)
    client.loop_start()
    return client

client = get_client()

print("=== 집으로 복귀 명령 테스트 ===\n")
print("※ mqtt_robot_simulator.py 가 실행 중이어야 합니다!\n")

# 현재 위치 설정
print("[1] 현재 위치를 (5.0, 3.0)으로 설정")
pose = {'x': 5.0, 'y': 3.0, 'theta': 0.0}
info = client.publish('robot/pose', json.dumps(pose))
info.wait_for_publish()
print("    → 웹에서 위치 (5.0, 3.0) 확인")

input("\n[Enter] 를 눌러 '집으로 복귀' 명령 전송...")

# 집으로 복귀 명령
print("[2] 집으로 복귀 명령 전송")
cmd = {'action': 'home'}
info = client.publish('robot/cmd/move', json.dumps(cmd))
info.wait_for_publish()
print("    → 시뮬레이터: '[명령] 집으로 이동!' 확인")
print("    → 시뮬레이터: 위치가 (0, 0)으로 이동")

time.sleep(3)

print("\n[3] 위치 (0, 0) 도착 확인")
pose = {'x': 0.0, 'y': 0.0, 'theta': 0.0}
info = client.publish('robot/pose', json.dumps(pose))
info.wait_for_publish()
print("    → 웹에서 위치 (0.0, 0.0) 확인")

time.sleep(0.5)
client.loop_stop()
client.disconnect()
print("\n테스트 완료!")
```

### 3.5 명령 종류

| 명령 | action 값 | 설명 |
|------|-----------|------|
| 집으로 복귀 | home | (0, 0) 위치로 이동 |
| 긴급 정지 | stop | 즉시 정지 |
| 충전 도킹 | dock | 충전 스테이션으로 이동 |
| 전진 | forward | 앞으로 이동 |
| 후진 | backward | 뒤로 이동 |
| 좌회전 | left | 왼쪽으로 회전 |
| 우회전 | right | 오른쪽으로 회전 |

### 3.6 확인 항목

| 단계 | 확인 위치 | 예상 결과 |
|------|-----------|-----------|
| 1 | 웹 홈/위치 화면 | 위치: (5.0, 3.0) |
| 2 | 시뮬레이터 터미널 | `[명령] 집으로 이동!` 출력 |
| 3 | 시뮬레이터 터미널 | 위치가 점점 (0, 0)으로 변경 |
| 4 | 웹 홈/위치 화면 | 위치: (0.0, 0.0) |

---

## 테스트 4: 현재 위치 좌표 수정

### 4.1 목적
로봇의 위치 좌표를 변경하면 웹에서 실시간으로 반영되는지 확인

### 4.2 통합 스크립트 사용

```bash
python mqtt_test.py 4
```

### 4.3 개별 Python 스크립트

파일: `test_position.py`

```python
#!/usr/bin/env python3
"""위치 좌표 수정 테스트"""
import paho.mqtt.client as mqtt
import json
import time

def get_client():
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        client = mqtt.Client()
    client.connect('localhost', 1883, 60)
    client.loop_start()
    return client

client = get_client()

print("=== 위치 좌표 수정 테스트 ===\n")

positions = [
    {'x': 0.0, 'y': 0.0, 'name': '홈 (원점)'},
    {'x': 5.0, 'y': 0.0, 'name': '오른쪽'},
    {'x': 5.0, 'y': 5.0, 'name': '오른쪽 위'},
    {'x': 0.0, 'y': 5.0, 'name': '위쪽'},
    {'x': -3.0, 'y': 2.0, 'name': '왼쪽 위'},
    {'x': 0.0, 'y': 0.0, 'name': '홈 복귀'},
]

for i, pos in enumerate(positions, 1):
    print(f"[{i}] {pos['name']}: ({pos['x']}, {pos['y']})")
    pose = {'x': pos['x'], 'y': pos['y'], 'theta': 0.0}
    info = client.publish('robot/pose', json.dumps(pose))
    info.wait_for_publish()
    print(f"    → 웹에서 위치 확인")

    if i < len(positions):
        input("\n[Enter] 를 눌러 다음 위치로...")
    print()

time.sleep(0.5)
client.loop_stop()
client.disconnect()
print("테스트 완료!")
```

### 4.4 확인 항목

| 단계 | 좌표 | 웹 표시 | DB 저장 |
|------|------|---------|---------|
| 1 | (0.0, 0.0) | (0.0, 0.0) | location: "(0.00, 0.00)" |
| 2 | (5.0, 0.0) | (5.0, 0.0) | location: "(5.00, 0.00)" |
| 3 | (5.0, 5.0) | (5.0, 5.0) | location: "(5.00, 5.00)" |

### 4.5 DB 저장 확인

```bash
curl -s http://localhost:8080/api/robots/me -H "Authorization: Bearer <토큰>"
# 응답: {"location": "(5.00, 3.00)", ...}
```

---

## 전체 테스트 (통합)

### 실행 명령

```bash
python mqtt_test.py 5
```

### 테스트 내용

| 순서 | 테스트 항목 | 전송 데이터 |
|------|------------|-------------|
| 1 | 배터리 | 80% |
| 2 | 일일 요약 | 산책 75분, 알림 4건 |
| 3 | 활동 이벤트 | "낙상 감지!" (DB 저장) |
| 4 | 위치 좌표 | (5.0, 3.0) |

### 확인 방법

1. http://localhost:5173 접속
2. test@test.com / test1234 로그인
3. 홈 화면 확인:
   - 배터리: 80%
   - 위치: (5.0, 3.0)
   - 오늘 하루: 산책시간, 이상감지
   - 최근 활동: 낙상 감지!
4. 기록 화면 확인:
   - 오늘 활동 로그 목록

---

## 문제 해결

### Q1: 데이터가 웹에 안 보여요

**원인**: WebSocket 연결 전에 데이터가 전송됨

**해결**:
1. 웹 페이지를 먼저 열고 로그인
2. 그 다음 테스트 스크립트 실행
3. 또는 새로고침 (F5) - API에서 DB 데이터 로드

### Q2: MQTT 연결 실패

**원인**: Mosquitto 브로커 미실행

**해결**:
```bash
# Mosquitto 실행 확인
netstat -an | findstr 1883

# 실행되지 않았다면
mosquitto
```

### Q3: 권한 오류 (401)

**원인**: 로그인 필요

**해결**:
1. test@test.com / test1234 로 로그인
2. 또는 API 테스트 시 토큰 포함

### Q4: 한 줄 명령어가 안 돼요

**원인**: 메시지 전송 전 스크립트 종료

**해결**: `time.sleep(0.5)` 추가
```bash
python -c "import paho.mqtt.client as mqtt;import json;import time;c=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2);c.connect('localhost',1883);c.publish('robot/status',json.dumps({'battery':80,'state':'IDLE','isOnline':True}));time.sleep(0.5)"
```

---

## MQTT 토픽 요약

| 토픽 | 방향 | 용도 | DB 저장 |
|------|------|------|---------|
| robot/status | 로봇→서버 | 배터리, 상태 | O (Robot) |
| robot/pose | 로봇→서버 | 위치 좌표 | O (Robot.location) |
| robot/summary | 로봇→서버 | 일일 요약 | X (실시간만) |
| robot/activity | 로봇→서버 | 활동 이벤트 | O (activity_logs) |
| robot/cmd/move | 서버→로봇 | 이동 명령 | X |
| robot/cmd/nav | 서버→로봇 | 좌표 이동 | X |

---

## 파일 목록

| 파일 | 위치 | 용도 |
|------|------|------|
| mqtt_test.py | C:\S14P11C101\ | 통합 테스트 스크립트 |
| mqtt_robot_simulator.py | ros2_ws\src\ | MQTT 로봇 시뮬레이터 |
| test_battery.py | 직접 생성 | 배터리 개별 테스트 |
| test_summary.py | 직접 생성 | 요약/이벤트 개별 테스트 |
| test_go_home.py | 직접 생성 | 복귀 명령 개별 테스트 |
| test_position.py | 직접 생성 | 위치 개별 테스트 |

---

*작성: Claude Code*
*최종 수정: 2026-01-30*
