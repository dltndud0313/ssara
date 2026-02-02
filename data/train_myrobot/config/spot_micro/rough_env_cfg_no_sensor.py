from isaaclab.utils import configclass
from .rough_env_cfg import SpotMicroRoughEnvCfg
from .spotmicro_quad import SPOTMICRO_QUAD_CFG

@configclass
class SpotMicroRoughNoSensorEnvCfg(SpotMicroRoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()

        # [수정] 로봇 설정 덮어쓰기
        # 부모 클래스에서 정의된 로봇이 있다면 교체, 없으면 새로 정의
        # 중복 소환 방지를 위해 replace() 사용 시 주의 (이미 부모에서 생성된 경우 덮어써야 함)
        
        # LocomotionVelocityRoughEnvCfg -> SpotMicroRoughEnvCfg -> NoSensorEnvCfg
        # 부모(rough_env_cfg.py)에서 이미 robot을 정의했지만, 
        # 우리의 통합된 SPOTMICRO_QUAD_CFG (Stiffness 80, pos 0.27 등 Phase 1 설정 포함)로 "확실하게" 교체
        # self.scene.robot = SPOTMICRO_QUAD_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")

        # --- Phase 1: 보상 가중치 조정 (2026-02-01) ---
        self.rewards.track_lin_vel_xy_exp.weight = 7.0 
        self.rewards.track_ang_vel_z_exp.weight = 3.5 
        self.rewards.flat_orientation_l2.weight = -0.5
        self.rewards.action_rate_l2.weight = -0.005

        # --- 센서 비활성화 ---
        self.scene.height_scanner = None
        # self.scene.contact_forces = None # Base Contact Termination을 위해 활성화

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
        # 몸체 접촉 종료 조건 활성화 (Blind Reset)
        # self.terminations.base_contact = None

@configclass
class SpotMicroRoughNoSensorEnvCfg_PLAY(SpotMicroRoughNoSensorEnvCfg):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        self.observations.policy.enable_corruption = False
        self.events.base_external_force_torque = None
        self.events.push_robot = None
