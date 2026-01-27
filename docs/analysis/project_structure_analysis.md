# 프로젝트 파일 구조 및 의존성 분석

이 문서는 `scripts/local_train.py`를 진입점으로 하는 프로젝트의 파일 의존성 및 구조를 설명합니다.

## 📂 파일 의존성 트리 (File Dependency Tree)

1.  **`scripts/local_train.py`** (메인 실행 파일)
    *   **역할**: Isaac Lab 환경을 초기화하고 RSL-RL 학습 루프를 실행하는 진입점입니다.
    *   **주요 의존성**:
        *   📄 `scripts/cli_args.py`: 커맨드 라인 인자 파싱 및 RSL-RL 설정 병합을 담당합니다.
        *   📂 `scripts/custom_quadruped_isaac/`: 커스텀 로봇 및 환경 설정이 포함된 패키지입니다.

2.  **`scripts/custom_quadruped_isaac/`** (커스텀 환경 패키지)
    *   **역할**: 커스텀 4족 보행 로봇(SpotMicroAI)을 위한 Gym 환경과 에이전트 설정을 정의하고 등록합니다.
    *   **구성 파일**:
        *   📄 `__init__.py`:
            *   Gym 환경 ID(`Isaac-Velocity-Flat-Custom-Quad-v0` 등)를 등록합니다.
            *   `env_cfg.py`와 `agent_cfg.py`를 임포트하여 진입점으로 연결합니다.
        *   📄 `env_cfg.py` (**핵심 설정**):
            *   **상속**: `isaaclab_tasks...LocomotionVelocityRoughEnvCfg` (Isaac Lab 기본 설정).
            *   **역할**: 로봇 자산 경로, 관절 설정, 보상(Reward), 종료(Termination) 조건을 정의합니다.
            *   **주요 변경**: 센서 경로(`.../Robot/SpotMicroAI/.*`)를 컨테이너 내부 Asset 구조에 맞게 수정했습니다.
        *   📄 `custom_quad.py`:
            *   **역할**: `ArticulationCfg`를 사용하여 로봇의 물리적 속성(관절 강성, 댐핑 등)과 **USD 에셋 경로**를 지정합니다.
            *   **USD 경로**: `/isaac-sim/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/custom_quadruped/robot.usd` (컨테이너 내부 파일 사용).
        *   📄 `agent_cfg.py`:
            *   **역할**: PPO(Proximal Policy Optimizeation) 알고리즘의 하이퍼파라미터를 설정합니다.
            *   **설정 값**: 네트워크 크기(`[512, 256, 128]`), 학습률, 배치 크기 등.

## 🔗 주요 연결 고리 및 데이터 흐름

1.  **실행 (Execution)**:
    사용자가 `./scripts/run_train.sh`를 실행하면 `local_train.py`가 호출됩니다.

2.  **초기화 (Initialization)**:
    `local_train.py`는 `custom_quadruped_isaac`를 임포트하여 Gym에 환경을 등록합니다.

3.  **환경 생성 (Environment Creation)**:
    `gym.make("Isaac-Velocity-Flat-Custom-Quad-v0")` 호출 시:
    *   `env_cfg.py` 설정이 로드됩니다.
    *   `custom_quad.py`에 지정된 USD 파일(`robot.usd`)이 시뮬레이터에 로드됩니다.
    *   이때, `env_cfg.py`에 정의된 센서 경로(`SpotMicroAI`)가 실제 로드된 USD 계층 구조와 일치해야 센서가 정상 작동합니다.

4.  **학습 (Training)**:
    `agent_cfg.py` 설정을 사용하여 RSL-RL 라이브러리의 `OnPolicyRunner`가 학습 루프를 돕니다.

### USD 파일 경로
*   `scripts/custom_quadruped_isaac/custom_quad.py`에 정의된 USD 파일 경로:
    `/isaac-sim/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/custom_quadruped/robot.usd`