# SpotMicro 학습 관리 및 시각화 가이드

이 문서는 SpotMicro 강화학습(RSL-RL) 프로세스를 제어하고 결과를 확인하는 방법을 설명합니다.

## 1. 학습 종료 (Stop Training)
학습을 안전하게 중단하려면 터미널에서 다음 키를 입력하십시오:

> **`Ctrl + C`**

*   시스템은 현재까지의 **학습 체크포인트(Model Checkpoint)**와 로그를 저장한 후 종료합니다.
*   종료 시 터미널 로그에 `Saving model to...` 메시지가 표시되는지 확인하십시오.

---

## 2. 학습 이어하기 (Resume Training)
중단된 학습을 이어서 진행하려면, 기존 `train.py` 실행 명령어에 `--resume` 옵션을 추가합니다.

### 기본 사용법 (최신 기록 불러오기)
가장 최근에 실행된 학습 기록을 자동으로 불러옵니다.

```bash
./isaaclab.sh -p ~/IsaacLab/scripts/reinforcement_learning/rsl_rl/train.py \
--task=Isaac-Velocity-Flat-Custom-Quad-v0 \
--num_envs=512 \
--resume
```

### 특정 기록 불러오기 (`--load_run`)
특정 날짜/시간의 학습 모델을 지정하여 불러옵니다. 폴더 이름은 `logs/rsl_rl/custom_quad_flat/` 아래의 날짜 폴더명입니다.

```bash
# 예시: 2026-01-28_05-01-39 기록에서 이어하기
./isaaclab.sh -p ~/IsaacLab/scripts/reinforcement_learning/rsl_rl/train.py \
--task=Isaac-Velocity-Flat-Custom-Quad-v0 \
--num_envs=512 \
--resume \
--load_run 2026-01-28_05-01-39
```

---

## 3. GUI로 확인하기 (Play / Visulaization)
`play.py` 스크립트를 사용하여 학습된 정책(Policy)이 실제로 로봇을 어떻게 제어하는지 시각적으로 확인할 수 있습니다.

### 실행 명령어
```bash
./isaaclab.sh -p ~/IsaacLab/scripts/reinforcement_learning/rsl_rl/play.py \
--task=Isaac-Velocity-Flat-Custom-Quad-Play-v0 \
--num_envs=50 \
--load_run 2026-01-28_05-01-39
```

### 주요 옵션 설명
*   **`--task=...-Play-v0`**: 시각화 전용 환경 설정을 사용합니다. (로봇 수 감소, 충돌/리셋 조건 완화 등)
*   **`--num_envs=50`**: 시각화 창에 띄울 로봇의 개수입니다. 너무 많으면 렌더링이 느려질 수 있습니다.
*   **`--load_run [폴더명]`**: 확인하고 싶은 학습 결과 폴더를 지정합니다. (지정하지 않으면 최신 폴더 사용)

---

## 4. 모델 저장 (Model Saving)
Isaac Lab(rsl_rl)에는 별도의 수동 저장 명령어(키 입력 등)는 없으며, **자동 저장** 시스템을 사용합니다.

### 저장 시점
1.  **자동 저장:** 설정된 주기(`save_interval`)마다 자동으로 체크포인트를 저장합니다.
    *   현재 설정: **50 Iteration** 마다 저장됨 (`config/spot_micro/agents/rsl_rl_ppo_cfg.py`)
2.  **종료 시 저장:** `Ctrl + C`를 눌러 학습을 중단하면, 즉시 현재 상태를 저장하고 종료합니다.

### 저장 위치
*   `logs/rsl_rl/custom_quad_flat/[날짜_시간]/model_*.pt` 파일로 저장됩니다.

---

## 5. 학습 그래프 확인 (Tensorboard)
학습 진행 상황(보상 변화, 승률 등)을 그래프로 확인하려면 Tensorboard를 사용합니다.

1.  **컨테이너 접속:**
    ```bash
    docker exec -it isaac-sim bash
    ```
2.  **Tensorboard 실행:**
    ```bash
    tensorboard --logdir /isaac-sim/IsaacLab/logs/rsl_rl --port 6006
    ```
3.  **브라우저 접속:** `http://localhost:6006`
    *   *참고: 컨테이너 실행 시 `-p 6006:6006` 옵션으로 포트가 개방되어 있어야 로컬에서 접속 가능합니다.*

---

## 6. Height Scanner & Contact Forces 비활성화 학습 (No Sensor)

height_scanner와 contact_forces 센서를 비활성화하여 **센서 없는 학습(blind policy)**을 진행할 수 있습니다.

### 변경 사항 (Proposed Changes)

#### [NEW] `flat_env_cfg_no_sensor.py`
`flat_env_cfg.py` 기반으로 contact_forces를 비활성화한 설정입니다.
- **센서 제거**: `contact_forces = None`
- **보상 제거**: `feet_air_time`, `undesired_contacts`, `feet_contact_forces`
- **종료 조건 제거**: `base_contact`

#### [NEW] `rough_env_cfg_no_sensor.py`
`rough_env_cfg.py` 기반으로 height_scanner와 contact_forces를 모두 비활성화한 설정입니다.
- **센서 제거**: `height_scanner = None`, `contact_forces = None`
- **관측 제거**: `height_scan = None`
- **보상 제거**: `feet_air_time`, `undesired_contacts`, `feet_contact_forces`
- **종료 조건 제거**: `base_contact`

### 검증 계획 (Verification Plan)

#### 자동 테스트 (Automated Tests)
컨테이너 내부에서 다음 명령어로 학습이 정상적으로 시작되는지 확인합니다.

```bash
docker exec -it isaac-sim /bin/bash -c "cd /isaac-sim/IsaacLab && ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task=Isaac-Velocity-Flat-NoSensor-Quad-v0 --num_envs=64 --max_iterations=10"
```

성공 기준:
- 오류 없이 10 iteration 완료
- 센서 관련 경고 없음

#### 수동 검증 (Manual Verification)
1. 학습 로그에서 `contact_forces` 또는 `height_scanner` 관련 오류가 없는지 확인
2. 보상 값이 정상적으로 출력되는지 확인

