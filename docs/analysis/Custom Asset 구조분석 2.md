# SpotMicro 설정 분석 보고서

## 개요
이 보고서는 `data/train_myrobot/config` 경로에 위치한 설정 파일들을 분석하며, 특히 `spot_micro` 디렉토리에 중점을 둡니다. 이 파일들은 Isaac Lab에서 SpotMicro 로봇을 위한 시뮬레이션 환경, 로봇 파라미터, 보상(rewards), 그리고 학습 에이전트(agents)를 정의합니다.

## 디렉토리 구조
- `spot_micro/`: SpotMicro의 메인 설정 디렉토리.
    - `__init__.py`: Gym 환경 레지스트리 등록 파일.
    - `flat_env_cfg.py`: 평지(flat) 지형 환경 설정.
    - `rough_env_cfg.py`: 거친(rough) 지형 환경 설정.
    - `spotmicro_quad.py`: 로봇 에셋 정의 (참조됨, 깊게 분석하지 않음).
    - `agents/`: 강화학습(RL) 에이전트 설정 포함.
        - `rsl_rl_ppo_cfg.py`: RSL-RL 라이브러리용 PPO 알고리즘 하이퍼파라미터.
        - `skrl_*.yaml`: SKRL 라이브러리용 설정 (대안 RL 백엔드).

## 환경 레지스트리 (`__init__.py`)
다음과 같은 환경들이 등록되어 있습니다:

| 환경 ID (Environment ID) | 설명 | 설정 진입점 (Config Entry Point) |
| :--- | :--- | :--- |
| `Isaac-Velocity-Flat-Custom-Quad-v0` | 평지 지형 학습 환경 | `CustomQuadFlatEnvCfg` |
| `Isaac-Velocity-Flat-Custom-Quad-Play-v0` | 평지 지형 시각화/Play 환경 | `CustomQuadFlatEnvCfg_PLAY` |
| `Isaac-Velocity-Rough-Custom-Quad-v0` | 거친 지형 학습 환경 | `CustomQuadRoughEnvCfg` |
| `Isaac-Velocity-Rough-Custom-Quad-Play-v0` | 거친 지형 시각화/Play 환경 | `CustomQuadRoughEnvCfg_PLAY` |

## 상세 설정 분석

### 1. 평지 환경 (`flat_env_cfg.py`)
**기반 클래스 (Base Class):** `SpotMicroFlatEnvCfg` (`LocomotionVelocityRoughEnvCfg` 상속)

- **지형 (Terrain):** "plane" (평지)으로 고정, 높이 스캐너(height scanner) 및 지형 커리큘럼 없음.
- **명령 (Commands):**
    - 선형 속도 X (Linear Velocity X): -0.6 ~ 0.6 m/s
    - 선형 속도 Y (Linear Velocity Y): -0.3 ~ 0.3 m/s
    - 각속도 Z (Angular Velocity Z): -1.0 ~ 1.0 rad/s
- **액션 (Actions):** 관절 위치 스케일(Joint position scale) **0.5** 설정.
- **보상 (Rewards):**
    - **추적 (Tracking):** `track_lin_vel_xy_exp` (5.0) 및 `track_ang_vel_z_exp` (2.5)에 높은 가중치.
    - **공중 체공 시간 (Air Time):** 가중치 2.0.
    - **페널티 (Penalties):** `undesired_contacts` (-5.0), `base_height` 편차 (-2.0), `flat_orientation` (-1.0)에 큰 페널티 부여.
- **이벤트 (Events):**
    - 베이스 질량(base mass)을 약간 무작위화 (-0.2kg ~ 1.0kg).
    - 로봇 관절을 기본 범위로 리셋.

### 2. 거친 지형 환경 (`rough_env_cfg.py`)
**기반 클래스 (Base Class):** `SpotMicroRoughEnvCfg`

- **커스텀 커리큘럼 (`spotmicro_velocity_curriculum`):**
    - 이동 거리 대 목표 거리 비율에 기반한 커스텀 승급/강등 로직 구현.
    - 목표 거리의 50% 이상 도달 시 승급; 10% 미만 시 강등.
- **지형 (Terrain):**
    - "boxes" 및 "random_rough" 서브 지형 사용. 높이 범위(0.025-0.1m) 및 노이즈(0.01-0.06m) 설정.
- **명령 (Commands):** 평지 환경에 비해 범위가 약간 축소됨 (예: 선형 속도 X +/- 0.4).
- **액션 (Actions):** 관절 위치 스케일 **1.0** 설정 (평지보다 높은 제어 권한).
- **보상 (안정성 위주 튜닝):**
    - **추적 (Tracking):** `track_lin_vel_xy_exp` 가중치 상향 (**7.0**).
    - **공중 체공 시간 (Air Time):** 가중치 **5.0**, 임계값 **0.15s** (소형 로봇에 최적화).
    - **베이스 높이 (Base Height):** 목표 높이 **0.19m**에서 벗어날 경우 강력한 페널티 (**-5.0**).
    - **발 접촉력 (Feet Contact Forces):** 일반적인 기본값에 비해 **페널티 가중치 대폭 감소** (-0.005). 거친 지형에서의 충격을 용인하기 위함으로 보임.
    - **페널티 (Penalties):** 떨림(jitter) 방지를 위해 `undesired_contacts`, `dof_acc`, `action_rate`에 강한 페널티.

## 에이전트 설정 (`agents/rsl_rl_ppo_cfg.py`)
**라이브러리:** RSL-RL

- **네트워크 구조 (Policy & Critic):**
    - 은닉층 (Hidden Layers): `[512, 256, 128]`
    - 활성화 함수 (Activation): `elu`
    - 초기 노이즈 표준편차 (Initial Noise Std): `1.0`
- **알고리즘 설정 (PPO):**
    - 환경 당 스텝 수 (Steps per Env): 24
    - 최대 반복 횟수 (Max Iterations): 40,000
    - 학습률 (Learning Rate): 1.0e-3 (Adaptive schedule)
    - 엔트로피 계수 (Entropy Coef): 0.0025
    - 감마 (Gamma): 0.99
    - 배치 크기 (Batch Size): 4 미니배치, 5 에포크.

## 주요 관찰 사항 (Key Observations)
1.  **안정화 집중 (Stabilization Focus):** "Rough" 설정은 안정성을 위해 상당한 튜닝이 이루어졌습니다. 특히 접촉력 페널티를 줄이고 베이스 높이 추적 페널티를 높인 점이 눈에 띕니다. 이는 로봇이 거친 지형에서 "폭주"하거나 심하게 떨리는(jittering) 문제가 있었음을 시사합니다.
2.  **커스텀 커리큘럼 (Custom Curriculum):** 지형 난이도 진행을 처리하기 위해 커스텀 로직이 도입되었습니다. 기본 커리큘럼이 이 특정 로봇에게 너무 공격적이거나 너무 느렸을 가능성이 있습니다.
3.  **액션 스케일링 (Action Scaling):** Flat(0.5)과 Rough(1.0) 사이에 액션 스케일링의 현저한 차이가 있습니다. 이는 거친 지형에서 더 강력하거나 큰 관절 움직임이 필요함을 의미합니다.

## 참고 파일 경로 (Reference File Paths)
분석에 사용된 주요 파일들의 절대 경로입니다:

### 설정 파일 (Configuration Files)
- **/home/actuating/workspaces/spotmicro/data/train_myrobot/config/spot_micro/__init__.py**
- **/home/actuating/workspaces/spotmicro/data/train_myrobot/config/spot_micro/flat_env_cfg.py**
- **/home/actuating/workspaces/spotmicro/data/train_myrobot/config/spot_micro/rough_env_cfg.py**
- **/home/actuating/workspaces/spotmicro/data/train_myrobot/config/spot_micro/agents/rsl_rl_ppo_cfg.py**
- **/home/actuating/workspaces/spotmicro/data/train_myrobot/config/spot_micro/agents/skrl_flat_ppo_cfg.yaml**
- **/home/actuating/workspaces/spotmicro/data/train_myrobot/config/spot_micro/agents/skrl_rough_ppo_cfg.yaml**

### 스크립트 파일 (Script Files)
- **/home/actuating/workspaces/spotmicro/scripts/run_container.sh**
- **/home/actuating/workspaces/spotmicro/scripts/train_myrobot.sh**

## 의존성 분석 (Dependency Analysis)
각 설정 파일에서 불러오는 외부 파일 및 모듈에 대한 분석입니다.

### 1. `flat_env_cfg.py` & `rough_env_cfg.py`
- **사용 중인 로봇 설정 (Robot Config):**
    - 코드: `from isaaclab_tasks.manager_based.locomotion.velocity.config.spotmicro_quadruped.spotmicro_quad import SPOTMICRO_QUAD_CFG`
    - **분석:** 현재 이 파일들은 **로컬 디렉토리에 있는 `spotmicro_quad.py`가 아니라**, `isaaclab_tasks` 패키지(라이브러리)에 포함된 원본 설정을 불러오고 있습니다.
    - **참고:** 로컬에 있는 `spotmicro_quad.py` 파일을 수정하더라도, import 경로를 `from . import spotmicro_quad` 등으로 변경하지 않는 한 반영되지 않습니다.

### 2. `spotmicro_quad.py` (로컬 파일)
- **USD 파일 경로:**
    - 코드: `usd_path="/workspace/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/spotmicro_quadruped/spot_micro/spot_micro.usd"`
    - **분석:** 이 경로는 **Docker 컨테이너 내부의 절대 경로**로 설정되어 있습니다.
    - **주의:** 로컬 환경에서 실행하거나 경로가 다른 경우 파일을 찾지 못할 수 있습니다. 현재 디렉토리에도 `spotmicro.usd` 등의 파일이 존재하므로 상황에 맞춰 경로 수정이 필요할 수 있습니다.

### 3. `agents/rsl_rl_ppo_cfg.py`
- **외부 모듈:** `isaaclab_rl.rsl_rl` 패키지의 `RslRlOnPolicyRunnerCfg` 등을 상속받아 사용합니다.
- 특정 파일 경로 의존성은 명시되어 있지 않습니다.
