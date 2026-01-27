# robot.usd 분석 보고서

## 1. 기본 정보
- **파일 경로**: `/isaac-sim/data/usd/robot.usd`
- **Up Axis**: Z
- **단위 (MetersPerUnit)**: 1.0 (미터 단위)

## 2. 계층 구조 (Hierarchy)
최상위 Prim 구조는 다음과 같습니다:
- `/World` (Xform)
- `/Environment` (Xform)
- `/Render`
- `/physicsScene` (PhysicsScene)
- `/SpotMicroAI` (Xform) - **로봇의 Root**
- `/visuals`, `/colliders`, `/meshes` (Scope)

## 3. 물리 속성 (Physics Properties)

### Articulation Root
- 경로: `/SpotMicroAI`
- 이 Prim에 `PhysicsArticulationRootAPI`가 적용되어 있어, 이 지점부터 관절 시스템이 시작됨을 의미합니다.

### Rigid Bodies (20개)
주요 링크들이 Rigid Body로 정의되어 있습니다:
- `base_link` (몸체)
- `front_link`, `rear_link`
- 각 다리 링크: `*_shoulder_link`, `*_leg_link`, `*_foot_link`, `*_toe_link`

### Joints (20개)
관절 구성은 다음과 같습니다:
- **다리 관절 (RevoluteJoint)**: 12개 (각 다리당 3개: shoulder, leg, foot)
  - 예: `front_left_shoulder`, `front_left_leg`, `front_left_foot`
- **고정 관절 (FixedJoint)**: 8개
  - 몸체 부착물: `base_front`, `base_lidar`, `base_rear`
  - 발끝: `*_toe` 링크들
  - **Root Joint**: `root_joint`

## 4. 주요 발견 사항 (Key Findings)
1.  **Root Joint 설정**: `/SpotMicroAI/root_joint`가 `PhysicsFixedJoint`로 설정되어 있습니다.
    -   **주의**: 로봇이 환경 내에서 자유롭게 이동해야 하는(Floating Base) 경우, Root Joint가 Fixed이면 로봇이 월드 원점에 고정되어 움직이지 못할 수 있습니다. 이동 로봇으로 사용하려면 이 조인트 구성을 확인하고 필요 시 수정(Virtual Joint 사용 또는 Fixed Joint 제거)해야 할 수 있습니다.
2.  **구조적 완성도**: 기본적으로 4족 보행 로봇(SpotMicro)의 형태를 갖추고 있으며, 각 다리에 3자유도(DOF)가 할당되어 있습니다.
3.  **Lidar**: `lidar_link`가 존재하며 `base_lidar` 조인트로 고정되어 있습니다.

## 5. 결론
`robot.usd` 파일은 SpotMicro 로봇의 물리적 정의를 포함하고 있으며, Isaac Sim에서 시뮬레이션하기 위한 기본적인 Articulation 구조를 갖추고 있습니다. 단, **이동 로봇으로서의 설정(Floating Base)**과 관련하여 `root_joint`의 Fixed 속성은 의도된 것인지 확인이 필요합니다.
