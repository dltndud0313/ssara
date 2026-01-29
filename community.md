# ROSBridge JSON 메시지 규격 (Spring Boot ↔ ROS2)

> 작성일: 2026-01-28
> 프로토콜: ROSBridge v2.0
> 용도: Spring Boot 서버에서 rosbridge_server와 통신하기 위한 JSON Payload 정의

---

## 목차

1. [연결 정보](#1-연결-정보)
2. [Subscribe 요청 (로봇 → 서버)](#2-subscribe-요청-로봇--서버)
3. [Publish 요청 (서버 → 로봇)](#3-publish-요청-서버--로봇)
4. [Service Call 요청](#4-service-call-요청)
5. [Action Goal 요청](#5-action-goal-요청)
6. [Java String 상수 정의](#6-java-string-상수-정의)

---

## 1. 연결 정보

### 1.1 rosbridge 서버 설정
| 항목 | 값 |
|------|-----|
| WebSocket URL | `ws://localhost:9090` |
| Protocol | ROSBridge v2.0 |
| 인코딩 | JSON (UTF-8) |

### 1.2 ROSBridge 기본 Operation
| op | 설명 |
|----|------|
| `subscribe` | 토픽 구독 시작 |
| `unsubscribe` | 토픽 구독 해제 |
| `publish` | 토픽에 메시지 발행 |
| `call_service` | 서비스 호출 |
| `send_action_goal` | 액션 목표 전송 |
| `cancel_action_goal` | 액션 취소 |

---

## 2. Subscribe 요청 (로봇 → 서버)

로봇의 상태 정보를 수신하기 위해 Spring Boot가 rosbridge에 보내는 구독 요청입니다.

---

### 2.1 로봇 상태 구독 (`/robot/status`)

**Topic:** `/robot/status`
**Message Type:** `std_msgs/msg/String` (JSON 문자열 포함)

#### Subscribe 요청
```json
{
  "op": "subscribe",
  "id": "subscribe:/robot/status",
  "topic": "/robot/status",
  "type": "std_msgs/msg/String",
  "throttle_rate": 1000,
  "queue_length": 1
}
```

#### 수신 메시지 형식
```json
{
  "op": "publish",
  "topic": "/robot/status",
  "msg": {
    "data": "{\"battery\":85,\"state\":\"IDLE\",\"isOnline\":true}"
  }
}
```

#### 파싱된 데이터 구조
```json
{
  "battery": 85,
  "state": "IDLE",
  "isOnline": true
}
```

| 필드 | 타입 | 설명 | 값 범위 |
|------|------|------|---------|
| battery | int | 배터리 잔량 (%) | 0 ~ 100 |
| state | string | 로봇 상태 | IDLE, MOVING, CHARGING, ERROR, DOCKING |
| isOnline | boolean | 온라인 여부 | true / false |

---

### 2.2 로봇 위치 구독 (`/robot/pose`)

**Topic:** `/robot/pose`
**Message Type:** `geometry_msgs/msg/Pose2D`

#### Subscribe 요청
```json
{
  "op": "subscribe",
  "id": "subscribe:/robot/pose",
  "topic": "/robot/pose",
  "type": "geometry_msgs/msg/Pose2D",
  "throttle_rate": 500,
  "queue_length": 1
}
```

#### 수신 메시지 형식
```json
{
  "op": "publish",
  "topic": "/robot/pose",
  "msg": {
    "x": 3.5,
    "y": 2.1,
    "theta": 1.57
  }
}
```

| 필드 | 타입 | 단위 | 설명 |
|------|------|------|------|
| x | float64 | meter | X 좌표 |
| y | float64 | meter | Y 좌표 |
| theta | float64 | radian | 방향각 (0 ~ 2π) |

---

### 2.3 배터리 상태 구독 (`/battery_state`)

**Topic:** `/battery_state`
**Message Type:** `sensor_msgs/msg/BatteryState`

#### Subscribe 요청
```json
{
  "op": "subscribe",
  "id": "subscribe:/battery_state",
  "topic": "/battery_state",
  "type": "sensor_msgs/msg/BatteryState",
  "throttle_rate": 5000,
  "queue_length": 1
}
```

#### 수신 메시지 형식
```json
{
  "op": "publish",
  "topic": "/battery_state",
  "msg": {
    "header": {
      "stamp": {
        "sec": 1706428800,
        "nanosec": 0
      },
      "frame_id": "battery"
    },
    "voltage": 12.6,
    "temperature": 25.0,
    "current": -0.5,
    "charge": 8.5,
    "capacity": 10.0,
    "design_capacity": 10.0,
    "percentage": 0.85,
    "power_supply_status": 2,
    "power_supply_health": 1,
    "power_supply_technology": 2,
    "present": true
  }
}
```

| 필드 | 타입 | 단위 | 설명 |
|------|------|------|------|
| percentage | float32 | 0.0~1.0 | 배터리 잔량 비율 |
| voltage | float32 | V | 전압 |
| current | float32 | A | 전류 (음수=방전, 양수=충전) |
| power_supply_status | uint8 | - | 0=UNKNOWN, 1=CHARGING, 2=DISCHARGING, 3=NOT_CHARGING, 4=FULL |

---

### 2.4 Odometry 구독 (`/odom`)

**Topic:** `/odom`
**Message Type:** `nav_msgs/msg/Odometry`

#### Subscribe 요청
```json
{
  "op": "subscribe",
  "id": "subscribe:/odom",
  "topic": "/odom",
  "type": "nav_msgs/msg/Odometry",
  "throttle_rate": 200,
  "queue_length": 1
}
```

#### 수신 메시지 형식
```json
{
  "op": "publish",
  "topic": "/odom",
  "msg": {
    "header": {
      "stamp": {"sec": 1706428800, "nanosec": 0},
      "frame_id": "odom"
    },
    "child_frame_id": "base_link",
    "pose": {
      "pose": {
        "position": {"x": 3.5, "y": 2.1, "z": 0.0},
        "orientation": {"x": 0.0, "y": 0.0, "z": 0.707, "w": 0.707}
      },
      "covariance": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    },
    "twist": {
      "twist": {
        "linear": {"x": 0.5, "y": 0.0, "z": 0.0},
        "angular": {"x": 0.0, "y": 0.0, "z": 0.1}
      },
      "covariance": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    }
  }
}
```

---

### 2.5 LiDAR 스캔 구독 (`/scan`)

**Topic:** `/scan`
**Message Type:** `sensor_msgs/msg/LaserScan`

#### Subscribe 요청
```json
{
  "op": "subscribe",
  "id": "subscribe:/scan",
  "topic": "/scan",
  "type": "sensor_msgs/msg/LaserScan",
  "throttle_rate": 1000,
  "queue_length": 1
}
```

#### 수신 메시지 형식 (간략화)
```json
{
  "op": "publish",
  "topic": "/scan",
  "msg": {
    "header": {
      "stamp": {"sec": 1706428800, "nanosec": 0},
      "frame_id": "laser"
    },
    "angle_min": -3.14159,
    "angle_max": 3.14159,
    "angle_increment": 0.0175,
    "time_increment": 0.0,
    "scan_time": 0.1,
    "range_min": 0.1,
    "range_max": 10.0,
    "ranges": [1.5, 1.6, 1.7, 2.0, "..."],
    "intensities": []
  }
}
```

---

### 2.6 범퍼 센서 구독 (`/bumper`)

**Topic:** `/bumper`
**Message Type:** `std_msgs/msg/Bool`

#### Subscribe 요청
```json
{
  "op": "subscribe",
  "id": "subscribe:/bumper",
  "topic": "/bumper",
  "type": "std_msgs/msg/Bool",
  "throttle_rate": 100,
  "queue_length": 1
}
```

#### 수신 메시지 형식
```json
{
  "op": "publish",
  "topic": "/bumper",
  "msg": {
    "data": true
  }
}
```

---

### 2.7 카메라 영상 구독 (`/camera/image_raw/compressed`)

**Topic:** `/camera/image_raw/compressed`
**Message Type:** `sensor_msgs/msg/CompressedImage`

#### Subscribe 요청
```json
{
  "op": "subscribe",
  "id": "subscribe:/camera/image_raw/compressed",
  "topic": "/camera/image_raw/compressed",
  "type": "sensor_msgs/msg/CompressedImage",
  "throttle_rate": 100,
  "queue_length": 1,
  "compression": "cbor"
}
```

#### 수신 메시지 형식
```json
{
  "op": "publish",
  "topic": "/camera/image_raw/compressed",
  "msg": {
    "header": {
      "stamp": {"sec": 1706428800, "nanosec": 0},
      "frame_id": "camera"
    },
    "format": "jpeg",
    "data": "<base64_encoded_image_data>"
  }
}
```

---

### 2.8 구독 해제 (공통)

```json
{
  "op": "unsubscribe",
  "id": "subscribe:/robot/status",
  "topic": "/robot/status"
}
```

---

## 3. Publish 요청 (서버 → 로봇)

Spring Boot 서버가 로봇을 제어하기 위해 rosbridge에 보내는 발행 요청입니다.

---

### 3.1 속도 제어 (`/cmd_vel`)

**Topic:** `/cmd_vel`
**Message Type:** `geometry_msgs/msg/Twist`

#### 전진 (0.5 m/s)
```json
{
  "op": "publish",
  "topic": "/cmd_vel",
  "msg": {
    "linear": {
      "x": 0.5,
      "y": 0.0,
      "z": 0.0
    },
    "angular": {
      "x": 0.0,
      "y": 0.0,
      "z": 0.0
    }
  }
}
```

#### 후진 (-0.3 m/s)
```json
{
  "op": "publish",
  "topic": "/cmd_vel",
  "msg": {
    "linear": {
      "x": -0.3,
      "y": 0.0,
      "z": 0.0
    },
    "angular": {
      "x": 0.0,
      "y": 0.0,
      "z": 0.0
    }
  }
}
```

#### 좌회전 (0.5 rad/s)
```json
{
  "op": "publish",
  "topic": "/cmd_vel",
  "msg": {
    "linear": {
      "x": 0.0,
      "y": 0.0,
      "z": 0.0
    },
    "angular": {
      "x": 0.0,
      "y": 0.0,
      "z": 0.5
    }
  }
}
```

#### 우회전 (-0.5 rad/s)
```json
{
  "op": "publish",
  "topic": "/cmd_vel",
  "msg": {
    "linear": {
      "x": 0.0,
      "y": 0.0,
      "z": 0.0
    },
    "angular": {
      "x": 0.0,
      "y": 0.0,
      "z": -0.5
    }
  }
}
```

#### 전진 + 좌회전 (커브)
```json
{
  "op": "publish",
  "topic": "/cmd_vel",
  "msg": {
    "linear": {
      "x": 0.3,
      "y": 0.0,
      "z": 0.0
    },
    "angular": {
      "x": 0.0,
      "y": 0.0,
      "z": 0.2
    }
  }
}
```

#### 정지 (Emergency Stop)
```json
{
  "op": "publish",
  "topic": "/cmd_vel",
  "msg": {
    "linear": {
      "x": 0.0,
      "y": 0.0,
      "z": 0.0
    },
    "angular": {
      "x": 0.0,
      "y": 0.0,
      "z": 0.0
    }
  }
}
```

| 파라미터 | 범위 | 단위 | 설명 |
|----------|------|------|------|
| linear.x | -1.0 ~ 1.0 | m/s | 전진(+) / 후진(-) |
| linear.y | 0.0 | m/s | (일반적으로 사용 안함) |
| linear.z | 0.0 | m/s | (일반적으로 사용 안함) |
| angular.x | 0.0 | rad/s | (일반적으로 사용 안함) |
| angular.y | 0.0 | rad/s | (일반적으로 사용 안함) |
| angular.z | -1.0 ~ 1.0 | rad/s | 좌회전(+) / 우회전(-) |

---

### 3.2 토픽 Advertise (발행 전 등록)

토픽 발행 전에 한 번 등록하면 성능이 향상됩니다.

```json
{
  "op": "advertise",
  "id": "advertise:/cmd_vel",
  "topic": "/cmd_vel",
  "type": "geometry_msgs/msg/Twist"
}
```

#### Unadvertise (등록 해제)
```json
{
  "op": "unadvertise",
  "id": "advertise:/cmd_vel",
  "topic": "/cmd_vel"
}
```

---

## 4. Service Call 요청

---

### 4.1 집으로 복귀 서비스 (`/go_home`)

**Service:** `/go_home`
**Service Type:** `std_srvs/srv/Trigger`

#### 요청
```json
{
  "op": "call_service",
  "id": "call_service:/go_home:1",
  "service": "/go_home",
  "type": "std_srvs/srv/Trigger",
  "args": {}
}
```

#### 응답
```json
{
  "op": "service_response",
  "id": "call_service:/go_home:1",
  "service": "/go_home",
  "values": {
    "success": true,
    "message": "Navigating to home position"
  },
  "result": true
}
```

---

### 4.2 충전 스테이션 도킹 (`/dock`)

**Service:** `/dock`
**Service Type:** `std_srvs/srv/Trigger`

#### 요청
```json
{
  "op": "call_service",
  "id": "call_service:/dock:1",
  "service": "/dock",
  "type": "std_srvs/srv/Trigger",
  "args": {}
}
```

---

### 4.3 긴급 정지 (`/emergency_stop`)

**Service:** `/emergency_stop`
**Service Type:** `std_srvs/srv/Trigger`

#### 요청
```json
{
  "op": "call_service",
  "id": "call_service:/emergency_stop:1",
  "service": "/emergency_stop",
  "type": "std_srvs/srv/Trigger",
  "args": {}
}
```

---

## 5. Action Goal 요청

Nav2 Navigation을 위한 Action 요청입니다.

---

### 5.1 좌표 이동 (`/navigate_to_pose`)

**Action:** `/navigate_to_pose`
**Action Type:** `nav2_msgs/action/NavigateToPose`

#### Goal 전송
```json
{
  "op": "send_action_goal",
  "id": "action:/navigate_to_pose:1",
  "action": "/navigate_to_pose",
  "action_type": "nav2_msgs/action/NavigateToPose",
  "goal": {
    "pose": {
      "header": {
        "stamp": {
          "sec": 0,
          "nanosec": 0
        },
        "frame_id": "map"
      },
      "pose": {
        "position": {
          "x": 5.0,
          "y": 3.0,
          "z": 0.0
        },
        "orientation": {
          "x": 0.0,
          "y": 0.0,
          "z": 0.0,
          "w": 1.0
        }
      }
    },
    "behavior_tree": ""
  },
  "feedback": true,
  "result": true
}
```

#### Feedback 수신
```json
{
  "op": "action_feedback",
  "id": "action:/navigate_to_pose:1",
  "action": "/navigate_to_pose",
  "values": {
    "current_pose": {
      "header": {"frame_id": "map"},
      "pose": {
        "position": {"x": 3.2, "y": 2.5, "z": 0.0},
        "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
      }
    },
    "navigation_time": {"sec": 5, "nanosec": 0},
    "estimated_time_remaining": {"sec": 10, "nanosec": 0},
    "number_of_recoveries": 0,
    "distance_remaining": 2.5
  }
}
```

#### Result 수신
```json
{
  "op": "action_result",
  "id": "action:/navigate_to_pose:1",
  "action": "/navigate_to_pose",
  "values": {},
  "status": "SUCCEEDED"
}
```

| status | 설명 |
|--------|------|
| SUCCEEDED | 목표 도달 성공 |
| ABORTED | 중단됨 |
| CANCELED | 취소됨 |

---

### 5.2 이동 취소

```json
{
  "op": "cancel_action_goal",
  "id": "action:/navigate_to_pose:1",
  "action": "/navigate_to_pose"
}
```

---

### 5.3 특정 좌표로 이동 예시

#### 집 위치 (0, 0)
```json
{
  "op": "send_action_goal",
  "id": "action:/navigate_to_pose:home",
  "action": "/navigate_to_pose",
  "action_type": "nav2_msgs/action/NavigateToPose",
  "goal": {
    "pose": {
      "header": {"stamp": {"sec": 0, "nanosec": 0}, "frame_id": "map"},
      "pose": {
        "position": {"x": 0.0, "y": 0.0, "z": 0.0},
        "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
      }
    },
    "behavior_tree": ""
  },
  "feedback": true,
  "result": true
}
```

#### 충전 스테이션 (-1, 0)
```json
{
  "op": "send_action_goal",
  "id": "action:/navigate_to_pose:charging",
  "action": "/navigate_to_pose",
  "action_type": "nav2_msgs/action/NavigateToPose",
  "goal": {
    "pose": {
      "header": {"stamp": {"sec": 0, "nanosec": 0}, "frame_id": "map"},
      "pose": {
        "position": {"x": -1.0, "y": 0.0, "z": 0.0},
        "orientation": {"x": 0.0, "y": 0.0, "z": 1.0, "w": 0.0}
      }
    },
    "behavior_tree": ""
  },
  "feedback": true,
  "result": true
}
```

---

## 6. Java String 상수 정의

Spring Boot에서 바로 사용할 수 있는 Java 상수 클래스입니다.

```java
package com.gae.server.global.rosbridge;

public class RosbridgeMessages {

    // ==================== Subscribe 요청 ====================

    public static final String SUBSCRIBE_ROBOT_STATUS = """
        {
          "op": "subscribe",
          "id": "subscribe:/robot/status",
          "topic": "/robot/status",
          "type": "std_msgs/msg/String",
          "throttle_rate": 1000,
          "queue_length": 1
        }
        """;

    public static final String SUBSCRIBE_ROBOT_POSE = """
        {
          "op": "subscribe",
          "id": "subscribe:/robot/pose",
          "topic": "/robot/pose",
          "type": "geometry_msgs/msg/Pose2D",
          "throttle_rate": 500,
          "queue_length": 1
        }
        """;

    public static final String SUBSCRIBE_BATTERY_STATE = """
        {
          "op": "subscribe",
          "id": "subscribe:/battery_state",
          "topic": "/battery_state",
          "type": "sensor_msgs/msg/BatteryState",
          "throttle_rate": 5000,
          "queue_length": 1
        }
        """;

    public static final String SUBSCRIBE_ODOM = """
        {
          "op": "subscribe",
          "id": "subscribe:/odom",
          "topic": "/odom",
          "type": "nav_msgs/msg/Odometry",
          "throttle_rate": 200,
          "queue_length": 1
        }
        """;

    public static final String SUBSCRIBE_BUMPER = """
        {
          "op": "subscribe",
          "id": "subscribe:/bumper",
          "topic": "/bumper",
          "type": "std_msgs/msg/Bool",
          "throttle_rate": 100,
          "queue_length": 1
        }
        """;

    // ==================== Advertise 요청 ====================

    public static final String ADVERTISE_CMD_VEL = """
        {
          "op": "advertise",
          "id": "advertise:/cmd_vel",
          "topic": "/cmd_vel",
          "type": "geometry_msgs/msg/Twist"
        }
        """;

    // ==================== Publish 템플릿 ====================

    /**
     * 속도 제어 메시지 생성
     * @param linearX 전진/후진 속도 (-1.0 ~ 1.0 m/s)
     * @param angularZ 회전 속도 (-1.0 ~ 1.0 rad/s)
     */
    public static String createCmdVel(double linearX, double angularZ) {
        return String.format("""
            {
              "op": "publish",
              "topic": "/cmd_vel",
              "msg": {
                "linear": {"x": %.2f, "y": 0.0, "z": 0.0},
                "angular": {"x": 0.0, "y": 0.0, "z": %.2f}
              }
            }
            """, linearX, angularZ);
    }

    /**
     * 정지 명령
     */
    public static final String CMD_VEL_STOP = """
        {
          "op": "publish",
          "topic": "/cmd_vel",
          "msg": {
            "linear": {"x": 0.0, "y": 0.0, "z": 0.0},
            "angular": {"x": 0.0, "y": 0.0, "z": 0.0}
          }
        }
        """;

    /**
     * 좌표 이동 Goal 생성
     * @param goalId 고유 ID
     * @param x 목표 X 좌표
     * @param y 목표 Y 좌표
     * @param yaw 목표 방향 (radian)
     */
    public static String createNavigateGoal(String goalId, double x, double y, double yaw) {
        double qz = Math.sin(yaw / 2.0);
        double qw = Math.cos(yaw / 2.0);

        return String.format("""
            {
              "op": "send_action_goal",
              "id": "action:/navigate_to_pose:%s",
              "action": "/navigate_to_pose",
              "action_type": "nav2_msgs/action/NavigateToPose",
              "goal": {
                "pose": {
                  "header": {"stamp": {"sec": 0, "nanosec": 0}, "frame_id": "map"},
                  "pose": {
                    "position": {"x": %.2f, "y": %.2f, "z": 0.0},
                    "orientation": {"x": 0.0, "y": 0.0, "z": %.4f, "w": %.4f}
                  }
                },
                "behavior_tree": ""
              },
              "feedback": true,
              "result": true
            }
            """, goalId, x, y, qz, qw);
    }

    /**
     * 집으로 복귀 Goal
     */
    public static final String NAVIGATE_HOME = """
        {
          "op": "send_action_goal",
          "id": "action:/navigate_to_pose:home",
          "action": "/navigate_to_pose",
          "action_type": "nav2_msgs/action/NavigateToPose",
          "goal": {
            "pose": {
              "header": {"stamp": {"sec": 0, "nanosec": 0}, "frame_id": "map"},
              "pose": {
                "position": {"x": 0.0, "y": 0.0, "z": 0.0},
                "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
              }
            },
            "behavior_tree": ""
          },
          "feedback": true,
          "result": true
        }
        """;

    /**
     * 이동 취소
     */
    public static String createCancelNavigation(String goalId) {
        return String.format("""
            {
              "op": "cancel_action_goal",
              "id": "action:/navigate_to_pose:%s",
              "action": "/navigate_to_pose"
            }
            """, goalId);
    }

    // ==================== Service Call ====================

    public static final String CALL_GO_HOME = """
        {
          "op": "call_service",
          "id": "call_service:/go_home:1",
          "service": "/go_home",
          "type": "std_srvs/srv/Trigger",
          "args": {}
        }
        """;

    public static final String CALL_EMERGENCY_STOP = """
        {
          "op": "call_service",
          "id": "call_service:/emergency_stop:1",
          "service": "/emergency_stop",
          "type": "std_srvs/srv/Trigger",
          "args": {}
        }
        """;

    public static final String CALL_DOCK = """
        {
          "op": "call_service",
          "id": "call_service:/dock:1",
          "service": "/dock",
          "type": "std_srvs/srv/Trigger",
          "args": {}
        }
        """;

    // ==================== Unsubscribe ====================

    public static String createUnsubscribe(String topic) {
        return String.format("""
            {
              "op": "unsubscribe",
              "id": "subscribe:%s",
              "topic": "%s"
            }
            """, topic, topic);
    }
}
```

---

## 7. 토픽/메시지 타입 요약표

### 7.1 Subscribe (로봇 → 서버)

| Topic | Message Type | 용도 | 주기 |
|-------|--------------|------|------|
| `/robot/status` | `std_msgs/msg/String` | 로봇 상태 (JSON) | 1000ms |
| `/robot/pose` | `geometry_msgs/msg/Pose2D` | 로봇 위치 | 500ms |
| `/battery_state` | `sensor_msgs/msg/BatteryState` | 배터리 정보 | 5000ms |
| `/odom` | `nav_msgs/msg/Odometry` | Odometry 정보 | 200ms |
| `/scan` | `sensor_msgs/msg/LaserScan` | LiDAR 데이터 | 1000ms |
| `/bumper` | `std_msgs/msg/Bool` | 충돌 감지 | 100ms |
| `/camera/image_raw/compressed` | `sensor_msgs/msg/CompressedImage` | 카메라 영상 | 100ms |

### 7.2 Publish (서버 → 로봇)

| Topic | Message Type | 용도 |
|-------|--------------|------|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | 속도 제어 |

### 7.3 Action (서버 → 로봇)

| Action | Action Type | 용도 |
|--------|-------------|------|
| `/navigate_to_pose` | `nav2_msgs/action/NavigateToPose` | 좌표 이동 |

### 7.4 Service (서버 → 로봇)

| Service | Service Type | 용도 |
|---------|--------------|------|
| `/go_home` | `std_srvs/srv/Trigger` | 집으로 복귀 |
| `/emergency_stop` | `std_srvs/srv/Trigger` | 긴급 정지 |
| `/dock` | `std_srvs/srv/Trigger` | 충전 도킹 |

---

## 8. 연결 Flow 다이어그램

```
┌──────────────────────────────────────────────────────────────────┐
│                        Spring Boot Server                         │
├──────────────────────────────────────────────────────────────────┤
│  1. WebSocket 연결: ws://localhost:9090                          │
│  2. Advertise: /cmd_vel                                          │
│  3. Subscribe: /robot/status, /robot/pose, /battery_state        │
│  4. 메시지 수신 대기...                                            │
└──────────────────────────────────────────────────────────────────┘
           │                                      ▲
           │ JSON Messages                        │ JSON Messages
           ▼                                      │
┌──────────────────────────────────────────────────────────────────┐
│                      rosbridge_server (9090)                      │
└──────────────────────────────────────────────────────────────────┘
           │                                      ▲
           │ ROS2 Topics                          │ ROS2 Topics
           ▼                                      │
┌──────────────────────────────────────────────────────────────────┐
│                         ROS2 Robot Node                           │
├──────────────────────────────────────────────────────────────────┤
│  Publishers:                                                      │
│    - /robot/status (String)                                       │
│    - /robot/pose (Pose2D)                                        │
│    - /battery_state (BatteryState)                               │
│  Subscribers:                                                     │
│    - /cmd_vel (Twist)                                            │
│  Actions:                                                         │
│    - /navigate_to_pose (NavigateToPose)                          │
└──────────────────────────────────────────────────────────────────┘
```

---

*문서 작성: Claude Code*
*프로토콜: ROSBridge v2.0*
*최종 수정: 2026-01-28*
