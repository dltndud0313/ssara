from isaaclab.utils import configclass
from .rough_env_cfg import SpotMicroRoughEnvCfg

@configclass
class SpotMicroRoughNoSensorEnvCfg(SpotMicroRoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()

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
