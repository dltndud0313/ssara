# SpotMicro 코드 리뷰 보고서 (Chung Review)

**날짜:** 2026-01-26  
**리뷰 대상:** `data/calibrated_train` 디렉토리 내 설정 파일들

이 문서는 SpotMicro 로봇의 강화학습 환경 설정을 담고 있는 Python 설정 파일들에 대한 상세 리뷰입니다.

---

## 1. 개요 및 파일 구조

이 디렉토리는 Isaac Lab 기반의 SpotMicro 로봇 학습을 위한 설정을 담고 있으며, 상속 구조를 통해 다양한 학습 시나리오(평지, 거친 지형, Blind Policy)를 지원합니다.

### 📂 파일 관계도
```
[locomotion.velocity.velocity_env_cfg] LocomotionVelocityRoughEnvCfg (Isaac Lab Base)
          ▲       ▲       ▲
          │       │       │ 상속
          │       │       └── [rough_student_env_cfg.py] SpotMicroRoughStudentEnvCfg (Blind Policy)
          │       │
          │       └────── [rough_env_cfg.py] SpotMicroRoughEnvCfg (Rough Terrain + Vision)
          │
          └────────────── [flat_env_cfg.py] SpotMicroFlatEnvCfg (Flat Terrain Baseline)

[spotmicro_quad.py] SPOTMICRO_QUAD_CFG (Robot Definition)
    │
    ├── 모든 환경 설정 파일(flat, rough, student)에서 로봇 정의로 import 됨
    └── USD 파일 경로, 관절/물리 속성, 초기 자세 정의
```

---

## 2. 파일별 상세 리뷰

### 🤖 1. `spotmicro_quad.py` (로봇 정의)
로봇의 물리적 속성과 USD 자산 경로를 정의하는 핵심 파일입니다.

- **주요 설정**:
  - `activate_contact_sensors=True`: 접촉 센서 활성화 (필수)
  - `linear/angular_damping=0.5`: 감쇠 설정 적절함
  - `stiffness=40.0`, `damping=5.0`: PD 제어기 게인값. 하드웨어 스펙과 일치하는지 확인 필요.
  - `effort_limit=2.5`: 토크 제한. 실제 모터 스펙 대비 여유가 있는지 확인 필요.

- **🚩 개선 필요 사항**:
  - **하드코딩된 경로**: ~~`usd_path`가 `/workspace/IsaacLab/...`으로 하드코딩 되어 있습니다. 컨테이너 내부 경로로 보이나, 실행 환경이 바뀌면 에러가 발생할 수 있습니다. `ISAACLAB_NUCLEUS_DIR` 혹은 상대 경로 사용을 권장합니다.~~
	  - 동적 경로 `usd_path=f"{os.path.dirname(__file__)}/spot_micro.usd"`로 변경

### 🏞️ 2. `flat_env_cfg.py` (평지 환경)
가장 기본적인 평지 주행 학습을 위한 설정입니다.

- **주요 설정**:
  - `terrain_type = "plane"`: 평지 지형 명시.
  - `height_scanner = None`: 평지이므로 높이 스캔 불필요, 자원 절약.
  - **속도 범위**: `vel_x` (±0.6), `vel_y` (±0.3). 초기 학습용으로 적절해 보입니다.

- **이슈 사항**:
  - `events.push_robot = None`: 외란(Push) 이벤트가 꺼져 있습니다. 강인한 정책 학습을 위해서는 추후 활성화를 고려해야 합니다.

### ⛰️ 3. `rough_env_cfg.py` (거친 지형 & 커리큘럼)
지형 인식(Vision/Height Scan)을 포함한 고난이도 환경입니다.

- **주요 설정**:
  - **커스텀 커리큘럼** (`spotmicro_velocity_curriculum`):
    - 승급 기준: 목표 거리의 50% 이상 주행
    - 강등 기준: 목표 거리의 10% 미만 주행
    - *의견*: 승/강등 기준이 다소 느슨할 수 있으나 안정적인 학습에는 유리할 수 있습니다.
  - **센서**: `height_scanner`가 활성화되어 지형 정보를 관측(`observations`)에 포함합니다.

- **보상 함수**:
  - `base_height_l2`: 목표 높이 0.19m (flat은 0.18m). 지형 요철을 고려해 약간 높게 잡은 것으로 보입니다.

### 🎓 4. `rough_student_env_cfg.py` (Blind Policy / Student)
센서 없이 고유수용성 감각(Proprioception)만으로 주행하는 Student 모델 학습용입니다.

- **구조적 특징**:
  - **Teacher-Student 학습**: `observations`가 Policy(Student)와 Critic(Teacher) 그룹으로 나뉘어 있습니다. (현재 코드는 Policy/Critic 구성이 동일함 - 의도된 사항인지 확인 필요)
  - **Blind Policy**: `height_scanner`가 `None`이며 관측 데이터에 지형 정보가 포함되지 않습니다.

- **⚠️ 중요 이슈 (Sensor Optimization)**:
  - **센서 범위 제한**: `contact_forces`의 `prim_path`가 `"{ENV_REGEX_NS}/Robot/.*foot.*"`로 설정되어 **발바닥 접촉만 감지**합니다. (다른 환경은 전체 바디 감지)
  - **영향**:
    - **장점**: 시뮬레이션 속도 향상 및 메모리 절약.
    - **단점**: 몸통이나 허벅지 등이 장애물에 부딪히는 것을 감지하지 못합니다. 따라서 `undesired_contacts`(원치 않는 접촉) 보상이 비활성화(`None`) 되어 있습니다. 로봇이 넘어져도 패널티를 덜 받을 수 있어, 넘어지는 자세를 학습할 위험이 있습니다.
    - **종료 조건**: `terminations.base_contact = None`으로 설정되어 있어, 몸통이 바닥에 닿아도 에피소드가 끝나지 않을 수 있습니다.

---

## 3. 센서 및 하드웨어 설정 심층 분석

### 📡 센서 설정 비교

| 환경 | Contact Sensor 범위 | Height Internal Scanner | 관측(Observation) 포함 여부 |
| :--- | :--- | :--- | :--- |
| **Flat** | Body 전체 (`Robot/.*`) | ❌ None | ❌ None |
| **Rough** | Body 전체 (`Robot/.*`) | ✅ `base_link` 기준 | ✅ Height Map 포함 |
| **Student** | **발 Only** (`.*foot.*`) | ❌ None | ❌ None (Blind) |

### 📉 5. 최적화: 센서 비활성화 (No Sensor)
성능 최적화 및 단순화된 학습(Blind Policy)을 위해 센서를 완전히 제거하는 옵션도 고려되었습니다.

- **목표**: `height_scanner`와 `contact_forces`를 비활성화하여 리소스 사용을 줄이고, 순수 proprioception 기반의 학습 가능성 탐색.
- **영향분석**:
  - `contact_forces` 제거 시: `feet_air_time`(공중 시간), `undesired_contacts`(충돌 감지), `feet_contact_forces`(충격 감지) 보상 함수 사용 불가. `base_contact` 종료 조건 사용 불가.
  - `height_scanner` 제거 시: 지형 정보 인식 불가 (Blind Agent).
- **구현 계획**: 별도의 설정 파일 (`*_no_sensor.py`)로 분리하여 관리.


### 🛠️ 하드웨어 매핑 점검
- **관절 이름 (Regex)**: `.*_shoulder`, `.*_leg`, `.*_foot`
- **링크 이름**: `base_link` vs `base`
  - 코드 전반에서 `base_link`를 사용 중입니다. 실제 USD 파일 내의 Root Link 이름이 `base_link`인지 반드시 확인해야 합니다. 만약 USD가 `base`라는 이름을 쓴다면 보상 함수가 작동하지 않거나 에러가 발생합니다.

---

## 4. 종합 제안 및 결론 (Recommendations)

1.  **USD 경로 수정 (우선순위 높음)**:
    - `spotmicro_quad.py`의 절대 경로를 환경 변수나 상대 경로로 변경하여 이식성을 확보하십시오.

2.  **Student 환경의 안전 장치 보완**:
    - `rough_student_env_cfg.py`에서 몸통 접촉 감지가 꺼져 있는 것은 위험할 수 있습니다. 메모리 문제가 심각하지 않다면 접촉 센서 범위를 전체(`Robot/.*`)로 되돌리고 `undesired_contacts` 보상과 `base_contact` 종료 조건을 활성화하는 것을 권장합니다.

3.  **이름 규칙(Naming Convention) 확인**:
    - USD 파일의 `base_link` 이름 일치 여부를 `inspect_usd.py` 등으로 재확인하십시오. 불일치 시 학습이 전혀 되지 않을 수 있습니다.

4.  **관측 공간 차별화**:
    - `rough_student_env_cfg.py`에서 Teacher(Critic)는 지형 정보나 특권 정보(Privileged Info)를 더 볼 수 있어야 Student를 잘 가르칠 수 있습니다. 현재 Policy와 Critic의 관측이 동일해 보입니다. 확인이 필요합니다.
