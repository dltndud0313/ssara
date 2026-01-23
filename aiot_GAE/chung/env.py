# env.py
from __future__ import annotations # 반드시 맨 첫 줄에 위치해야 함

import torch
import isaaclab.sim as sim_utils
import isaaclab.envs.mdp as mdp
from isaaclab.assets import AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnv, ManagerBasedRLEnvCfg
from isaaclab.managers import (
    ActionTermCfg, ObservationGroupCfg, ObservationTermCfg, 
    RewardTermCfg, SceneEntityCfg, TerminationTermCfg, EventTermCfg
)
from isaaclab.scene import InteractiveSceneCfg 
from isaaclab.utils import configclass

# config.py에서 로봇 설정 가져오기
from spot_micro_config import SPOT_MICRO_CFG

def custom_base_height_exp(env: ManagerBasedRLEnv, target_height: float, std: float, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    """몸체 높이를 지수 함수(Exponential) 형태로 보상합니다."""
    # 로봇 자산 가져오기
    asset = env.scene[asset_cfg.name]
    # 현재 몸체 높이 (z축 좌표)
    current_height = asset.data.root_pos_w[:, 2]
    # 오차 계산 및 지수 보상 적용: exp(-|error|^2 / std^2)
    return torch.exp(-torch.square(current_height - target_height) / (std ** 2))

@configclass
class ActionsCfg:
    """로봇의 행동 정의"""
    joint_pos = mdp.JointPositionActionCfg(
        asset_name="robot", joint_names=[".*"], 
        scale=0.5, # 0.5 스케일로 정교한 제어 유도
        use_default_offset=True
    )

@configclass
class ObservationsCfg:
    """로봇의 관측 정의"""
    @configclass
    class PolicyCfg(ObservationGroupCfg):
        joint_vel = ObservationTermCfg(func=mdp.joint_vel_rel, scale=0.1)
        joint_pos = ObservationTermCfg(func=mdp.joint_pos_rel, scale=1.0)
        base_lin_vel = ObservationTermCfg(func=mdp.base_lin_vel, scale=2.0)
        base_ang_vel = ObservationTermCfg(func=mdp.base_ang_vel, scale=0.25)
        projected_gravity = ObservationTermCfg(func=mdp.projected_gravity, scale=1.0)
        velocity_commands = ObservationTermCfg(
            func=mdp.generated_commands, scale=1.0, params={"command_name": "base_velocity"}
        )
        def __post_init__(self):
            self.enable_corruption = True
            self.concatenate_terms = True
    policy: PolicyCfg = PolicyCfg()

@configclass
class RewardsCfg:
    """보상 정의 (지수형 높이 보상 적용)"""
    alive = RewardTermCfg(func=mdp.is_alive, weight=1.0)
    
    # 명령 속도 추종 (std=0.2로 엄격하게)
    track_lin_vel_xy_exp = RewardTermCfg(
        func=mdp.track_lin_vel_xy_exp, weight=20.0, 
        params={"std": 0.2, "command_name": "base_velocity"} 
    )
    track_ang_vel_z_exp = RewardTermCfg(
        func=mdp.track_ang_vel_z_exp, weight=10.0, 
        params={"std": 0.2, "command_name": "base_velocity"} 
    )

    # [핵심] 커스텀 지수형 높이 보상
    # 23cm에 가까울수록 점수가 15점에 수렴하여 배를 땅에서 떼게 만듭니다.
    base_height_exp = RewardTermCfg(
        func=custom_base_height_exp, 
        weight=15.0, 
        params={
            "target_height": 0.23, 
            "std": 0.1, # 10cm 오차 범위를 넘어가면 점수가 하락
            "asset_cfg": SceneEntityCfg("robot")
        }
    )
    
    flat_orientation_l2 = RewardTermCfg(func=mdp.flat_orientation_l2, weight=-5.0)
    action_rate_l2 = RewardTermCfg(func=mdp.action_rate_l2, weight=-0.1) 
    joint_pos_limits = RewardTermCfg(func=mdp.joint_pos_limits, weight=-10.0)
    joint_vel_l2 = RewardTermCfg(func=mdp.joint_vel_l2, weight=-0.01)
    joint_torques_l2 = RewardTermCfg(func=mdp.joint_torques_l2, weight=-0.0001)

@configclass
class TerminationsCfg:
    """종료 조건"""
    time_out = TerminationTermCfg(func=mdp.time_out, time_out=True)
    bad_orientation = TerminationTermCfg(func=mdp.bad_orientation, params={"limit_angle": 0.5}) 
    base_height_termination = TerminationTermCfg(func=mdp.root_height_below_minimum, params={"minimum_height": 0.12})

@configclass
class CommandsCfg:
    base_velocity = mdp.UniformVelocityCommandCfg(
        asset_name="robot", resampling_time_range=(5.0, 10.0), debug_vis=True,
        ranges=mdp.UniformVelocityCommandCfg.Ranges(
            lin_vel_x=(-0.3, 0.3), lin_vel_y=(-0.2, 0.2), ang_vel_z=(-0.5, 0.5)  
        ),
    )

@configclass
class EventCfg:
    """이벤트 정의"""
    physics_material = EventTermCfg(
        func=mdp.randomize_rigid_body_material, mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=".*"),
            "static_friction_range": (0.8, 1.2), "dynamic_friction_range": (0.6, 1.0),
            "restitution_range": (0.0, 0.0), "num_buckets": 64,
        },
    )
    reset_base = EventTermCfg(
        func=mdp.reset_root_state_uniform, mode="reset",
        params={
            "pose_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5), "yaw": (-3.14, 3.14)},
            "velocity_range": {
                "x": (-0.001, 0.001), "y": (-0.001, 0.001), "z": (-0.001, 0.001),
                "roll": (-0.001, 0.001), "pitch": (-0.001, 0.001), "yaw": (-0.001, 0.001),
            },
        },
    )
    reset_robot_joints = EventTermCfg(
        func=mdp.reset_joints_by_scale, mode="reset",
        params={"position_range": (0.9, 1.1), "velocity_range": (0.0, 0.0)},
    )
    randomize_mass = EventTermCfg(
        func=mdp.randomize_rigid_body_mass, mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=".*"),
            "mass_distribution_params": (0.9, 1.1), "operation": "scale",
        },
    )

@configclass
class SpotMicroSceneCfg(InteractiveSceneCfg):
    """시뮬레이션 장면 구성"""
    robot = SPOT_MICRO_CFG
    terrain = AssetBaseCfg(prim_path="/World/ground", spawn=sim_utils.GroundPlaneCfg())
    light = AssetBaseCfg(prim_path="/World/light", spawn=sim_utils.DistantLightCfg(intensity=3000.0, angle=75.0))

@configclass
class SpotMicroRoughEnvCfg(ManagerBasedRLEnvCfg):
    """최종 환경 설정"""
    decimation = 4
    episode_length_s = 20.0
    scene: SpotMicroSceneCfg = SpotMicroSceneCfg(num_envs=2048, env_spacing=2.5)
    observations = ObservationsCfg(); actions = ActionsCfg()
    rewards = RewardsCfg(); commands = CommandsCfg()
    terminations = TerminationsCfg(); events = EventCfg()