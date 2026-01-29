# SpotMicro 로봇 설정 통합 계획 (Custom Asset 구조분석 3)

## 1. 개요
기존에 `spotmicro_quad.py` 파일로 분리되어 있던 로봇 설정(`ArticulationCfg`)을 각 환경 설정 파일(`flat_env_cfg.py`, `rough_env_cfg.py`)에 직접 통합합니다. 이를 통해 환경별 독립적인 로봇 튜닝이 가능해지고 파일 참조 의존성을 단순화합니다.

## 2. 통합 대상 파일
- **Source**: `data/train_myrobot/config/spot_micro/spotmicro_quad.py`
- **Target 1**: `data/train_myrobot/config/spot_micro/flat_env_cfg.py`
- **Target 2**: `data/train_myrobot/config/spot_micro/rough_env_cfg.py`
- **Target 3**: `data/train_myrobot/config/spot_micro/flat_env_cfg_no_sensor.py`
- **Target 4**: `data/train_myrobot/config/spot_micro/rough_env_cfg_no_sensor.py`

## 3. 주요 변경 사항
`spotmicro_quad.py`의 내용을 각 Target 파일의 상단에 삽입하고, 상세한 주석을 추가합니다.

### 3.1. 로봇 설정 코드 (`SPOTMICRO_QUAD_CFG`)
다음 코드가 각 파일에 포함됩니다.

```python
import os
import isaaclab.sim as sim_utils
from isaaclab.actuators import IdealPDActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg

# [통합] 로봇 정의 (기존 spotmicro_quad.py 내용)
# 이 설정은 로봇의 물리적 속성, 초기 자세, USD 파일 경로 등을 정의합니다.
SPOTMICRO_QUAD_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        # USD 파일 경로: 현재 파일 위치를 기준으로 상대 경로 설정
        usd_path=f"{os.path.dirname(__file__)}/spot_micro.usd",
        
        # [중요] 접촉 센서 활성화 여부
        # True로 설정해야 발바닥 접촉력 등을 감지할 수 있습니다.
        # *_no_sensor.py 환경에서는 이 설정이 True여도 코드 레벨에서 센서를 비활성화합니다.
        activate_contact_sensors=True,
        
        # Rigid Body (강체) 물리 속성
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            rigid_body_enabled=True,
            disable_gravity=False,
            linear_damping=0.5,  # 선형 감쇠: 움직임 저항
            angular_damping=0.5, # 회전 감쇠: 회전 저항
            max_linear_velocity=1000.0,
            max_angular_velocity=1000.0,
            max_depenetration_velocity=1.0,
        ),
        # Articulation (관절) 물리 속성
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False, # 자가 충돌 방지 (성능 향상)
            solver_position_iteration_count=4,
            solver_velocity_iteration_count=0,
            fix_root_link=False, # 로봇을 고정하지 않음 (자유 이동)
        ),
    ),
    # 초기 상태 (Reset 시 적용되는 자세)
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.27), # 초기 높이 0.27m
        joint_pos={
            ".*_shoulder": 0.0,
            ".*_leg": 0.8,
            ".*_foot": -1.0,
        },
        joint_vel={".*": 0.0}, # 초기 속도 0
    ),
    soft_joint_pos_limit_factor=0.9, # 관절 가동 범위 제한 (안전율 0.9)
    # 액추에이터 (모터) 설정
    actuators={
        "base_legs": IdealPDActuatorCfg(
            joint_names_expr=[".*_leg", ".*_foot", ".*_shoulder"],
            stiffness=40.0,  # P gain: 위치 복원력 (강성)
            damping=5.0,     # D gain: 속도 저항력 (감쇠)
            effort_limit=2.5, # 최대 토크 제한
            velocity_limit=6.0, # 최대 속도 제한
        ),
    },
)
```

## 4. 기대 효과
1.  **독립성**: Rough 환경에서는 모터 Damping을 높이고, Flat 환경에서는 낮추는 등 환경 특성에 맞는 하드웨어 튜닝이 가능해집니다.
2.  **직관성**: 로봇 설정이 환경 파일 내에 있어, 환경 설정을 볼 때 로봇 스펙도 함께 확인할 수 있습니다.
3.  **안전성**: 외부 파일 수정으로 인한 의도치 않은 다른 환경의 설정 변경을 방지합니다.

## 5. 검증 계획
통합 후 `Isaac-Velocity-Flat-NoSensor-Quad-v0` 환경에서 학습을 짧게 수행하여 USD 로드 및 물리 시뮬레이션이 정상 작동하는지 확인합니다.

## 6. 작업 결과 (Update)
`flat_env_cfg_no_sensor.py` 및 `rough_env_cfg_no_sensor.py` 파일에 대해 로봇 설정 통합 작업을 완료했습니다.

1. **로봇 설정 통합**: 각 파일 내에 `SPOTMICRO_QUAD_CFG`를 직접 정의하여 독립성을 확보했습니다.
2. **코드 적용**: `__post_init__` 메서드에서 `self.scene.robot`을 로컬 설정으로 덮어쓰도록 수정했습니다.
3. **검증**: 변경된 파일들에 대해 Python 문법 검사(Syntax Check)를 수행하여 오류가 없음을 확인했습니다.
