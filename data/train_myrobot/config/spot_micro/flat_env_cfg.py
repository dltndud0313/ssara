from isaaclab.utils import configclass
from isaaclab_tasks.manager_based.locomotion.velocity.velocity_env_cfg import LocomotionVelocityRoughEnvCfg
# [수정] 외부 파일 참조 제거
# from .spotmicro_quad import SPOTMICRO_QUAD_CFG 
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

from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.sensors import ContactSensorCfg
import isaaclab.envs.mdp as mdp

@configclass
class SpotMicroFlatEnvCfg(LocomotionVelocityRoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()

        # --- 로봇 및 센서 설정 ---
        self.scene.robot = SPOTMICRO_QUAD_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        self.scene.contact_forces = ContactSensorCfg(
            prim_path="{ENV_REGEX_NS}/Robot/.*", 
            history_length=3, 
            track_air_time=True
        )

        # 평지 지형 설정
        self.scene.terrain.terrain_type = "plane"
        self.scene.terrain.terrain_generator = None
        self.scene.height_scanner = None
        self.observations.policy.height_scan = None
        self.curriculum.terrain_levels = None

        # --- 동작 및 속도 범위 확장 ---
        self.actions.joint_pos.scale = 0.5
        self.commands.base_velocity.ranges.lin_vel_x = (-0.6, 0.6) 
        self.commands.base_velocity.ranges.lin_vel_y = (-0.3, 0.3) 
        self.commands.base_velocity.ranges.ang_vel_z = (-1.0, 1.0)

        # --- 이벤트 설정 (오류 수정: base -> base_link) ---
        self.events.push_robot = None
        self.events.add_base_mass.params["asset_cfg"].body_names = "base_link"
        self.events.add_base_mass.params["mass_distribution_params"] = (-0.2, 1.0)
        self.events.base_external_force_torque.params["asset_cfg"].body_names = "base_link"
        self.events.base_com.params["asset_cfg"].body_names = "base_link"
        self.events.reset_robot_joints.params["position_range"] = (1.0, 1.0)

        # --- 보상 설정 (움직임 중심 강화) ---
        self.rewards.track_lin_vel_xy_exp.weight = 5.0 
        self.rewards.track_ang_vel_z_exp.weight = 2.5  
        self.rewards.feet_air_time.weight = 2.0 
        self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_foot_link"

        # 오류 수정: .*THIGH -> .*_leg_link
        self.rewards.undesired_contacts = RewTerm(
            func=mdp.undesired_contacts,
            weight=-5.0,
            params={
                "sensor_cfg": SceneEntityCfg("contact_forces", 
                    body_names=["base_link", ".*_shoulder_link", ".*_leg_link"]),
                "threshold": 1.0,
            },
        )

        setattr(self.rewards, "lin_vel_z_l2", RewTerm(func=mdp.lin_vel_z_l2, weight=-0.5))
        setattr(self.rewards, "ang_vel_xy_l2", RewTerm(func=mdp.ang_vel_xy_l2, weight=-0.05))
        self.rewards.flat_orientation_l2.weight = -1.0
        
        setattr(self.rewards, "base_height_l2", RewTerm(
            func=mdp.base_height_l2,
            weight=-2.0,
            params={
                "target_height": 0.18,
                "asset_cfg": SceneEntityCfg("robot", body_names="base_link")
            },
        ))

        self.rewards.dof_torques_l2.weight = -0.00005 
        self.rewards.dof_acc_l2.weight = -1.0e-7      
        setattr(self.rewards, "action_rate_l2", RewTerm(func=mdp.action_rate_l2, weight=-0.01))
        setattr(self.rewards, "feet_contact_forces", RewTerm(
            func=mdp.contact_forces, 
            weight=-0.001,
            params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot_link"), "threshold": 10.0}
        ))

        self.terminations.base_contact.params["sensor_cfg"].body_names = "base_link"

# --- [추가] 시각화(Play)를 위한 전용 설정 클래스 ---
@configclass
class SpotMicroFlatEnvCfg_PLAY(SpotMicroFlatEnvCfg):
    def __post_init__(self) -> None:
        super().__post_init__()
        # 시각화를 위해 로봇 수와 간격 조정
        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        # 센서 데이터 노이즈(Corruption) 비활성화
        self.observations.policy.enable_corruption = False
        # 무작위 푸시 및 힘 이벤트 비활성화
        self.events.base_external_force_torque = None
        self.events.push_robot = None