# Isaac Sim GUI를 이용한 USD 파일 수정 가이드

이 문서는 Python 코드가 아닌, Isaac Sim GUI를 사용하여 `spot_micro.usd` 파일의 기본 속성(초기 위치, 관절 각도 등)을 직접 수정하고 저장하는 방법을 설명합니다.

이렇게 USD 파일 자체에 초기 상태(Initial State)를 "Baking" 해두면, 환경 설정 코드(`flat_env_cfg.py`)에서 `init_state` 설정을 줄이거나 제거할 수 있어 관리가 용이해집니다.

## 1. 컨테이너 실행

터미널에서 컨테이너를 실행합니다.

```bash
./scripts/run_container.sh
```

## 2. Isaac Sim 실행

컨테이너 내부 쉘에서 Isaac Sim GUI를 실행합니다.

```bash
./isaac-sim.sh
```
> **참고**: GUI 창이 뜨는 데 시간이 조금 걸릴 수 있습니다.

## 3. USD 파일 열기

Isaac Sim 메뉴에서 **File > Open**을 클릭하고, 아래 경로의 파일을 엽니다.

*   **경로**: `/isaac-sim/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/spot_micro/spot_micro.usd`

> **Note**: 위 경로는 컨테이너 내부의 마운트 경로입니다. 호스트 머신에서는 `workspaces/spotmicro/data/train_myrobot/config/spot_micro/spot_micro.usd`에 해당합니다.

## 4. 속성 수정 (Properties)

우측의 **Stage** 탭에서 로봇의 Root Prim(보통 `spot_micro` 또는 최상위 노드)을 선택하고, **Property** 탭에서 값을 수정합니다.

### 4.1. 초기 위치 설정 (Root Transform)
로봇이 바닥에 파묻히지 않도록 기본 높이를 설정합니다.

*   **Translate**: `Z` 값을 `0.27`로 변경 (단위: 미터)
    *   입력 예시: `Translate: (0, 0, 0.27)`

### 4.2. 관절 초기 각도 설정 (Joint Drives)
Stage 탭에서 각 관절(Joint)을 찾아 선택합니다. 보통 `Looks/Example/Joints` 등의 계층 구조 아래에 있거나, 검색창에서 `*joint` 등으로 검색할 수 있습니다.

각 관절의 `Drive` API가 적용되어 있다면 `Target Position`을, 혹은 `Angular Position` 값을 아래와 같이 수정합니다. (로봇의 "Standing Pose"를 만들기 위함입니다.)

*   **Shoulder Joints** (`*_shoulder`): `0.0`
*   **Leg Joints** (`*_leg`): `0.8` (약 45도)
*   **Foot Joints** (`*_foot`): `-1.0` (약 -57도)

> **팁**: 모든 관절을 하나씩 수정하기 힘들다면, 시뮬레이션 플레이 버튼을 누르기 전 상태(Edit Mode)가 바로 초기 상태로 저장되므로, 뷰포트에서 관절을 선택하고 기즈모(Gizmo)로 회전시켜 대략적인 자세를 잡아도 됩니다. 하지만 정확한 값을 입력하는 것을 권장합니다.

## 5. 저장 (Save)

수정이 완료되면 반드시 저장합니다.

*   **File > Save**

---

## 6. 확인 (Verification)

터미널에서 학습 스크립트를 실행하여, Python 코드의 `init_state` 설정 없이도 로봇이 올바른 자세로 생성되는지 확인합니다.

```bash
./scripts/train_myrobot.sh
```
(이때 `flat_env_cfg.py`의 `init_state` 블록은 주석 처리되어 있어야 순수 USD 설정값으로 테스트가 가능합니다.)
