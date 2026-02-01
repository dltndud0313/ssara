from isaaclab.utils import configclass
from .rough_env_cfg import SpotMicroRoughEnvCfg
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

@configclass
class SpotMicroRoughNoSensorEnvCfg(SpotMicroRoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()

        # [추가] 로봇 설정 덮어쓰기
        self.scene.robot = SPOTMICRO_QUAD_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")

        # --- 센서 비활성화 ---
        self.scene.height_scanner = None
        self.scene.contact_forces = None
        
        # Policy 관측에서 Height Scan 제거
        self.observations.policy.height_scan = None

        # --- 관련 보상 비활성화 ---
        # 센서 의존 보상 제거
        self.rewards.feet_air_time = None
        self.rewards.undesired_contacts = None
        
        # setattr로 추가된 보상 제거 (feet_contact_forces)
        if hasattr(self.rewards, "feet_contact_forces"):
            delattr(self.rewards, "feet_contact_forces")

        # --- 종료 조건 비활성화 ---
        # 몸체 접촉 종료 조건 제거 (Contact Sensor 의존)
        self.terminations.base_contact = None

@configclass
class SpotMicroRoughNoSensorEnvCfg_PLAY(SpotMicroRoughNoSensorEnvCfg):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        self.observations.policy.enable_corruption = False
        self.events.base_external_force_torque = None
        self.events.push_robot = None
