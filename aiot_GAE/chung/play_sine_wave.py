import argparse
from isaaclab.app import AppLauncher

# [1] Isaac Sim 앱 런처 설정
parser = argparse.ArgumentParser(description="Spot Micro Height Check with Auto Reset")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

# [2] 라이브러리 임포트
import torch
import math
import isaaclab.sim as sim_utils
from isaaclab.scene import InteractiveScene
from isaaclab.sim import SimulationContext
import sys
import os

# 경로 문제 해결
current_script_path = os.path.dirname(os.path.abspath(__file__))
isaac_lab_root = os.path.abspath(os.path.join(current_script_path, "../../../"))
if isaac_lab_root not in sys.path:
    sys.path.append(isaac_lab_root)

try:
    from my_projects.SpotMicroJetson.env import SpotMicroSceneCfg
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(current_script_path, "..")))
    from env import SpotMicroSceneCfg

def main():
    # [3] 시뮬레이션 설정 및 장면 생성
    sim_cfg = sim_utils.SimulationCfg(device=args_cli.device)
    sim = SimulationContext(sim_cfg)

    scene_cfg = SpotMicroSceneCfg(num_envs=1, env_spacing=2.0)
    scene = InteractiveScene(scene_cfg)

    sim.reset()
    robot = scene["robot"]
    
    # 타이머 관련 변수 초기화
    sim_time = 0.0
    last_reset_time = 0.0
    reset_interval = 5.0  # 리셋 간격 (초)

    print("\n" + "="*60)
    print(f"[INFO] 로봇 높이 측정 및 {reset_interval}초마다 리셋 시작")
    print("="*60 + "\n")

    while simulation_app.is_running():
        # [4] 5초마다 리셋 로직
        if sim_time - last_reset_time >= reset_interval:
            print(f"\n[INFO] {reset_interval}초 경과: 시뮬레이션을 리셋합니다.          ")
            sim.reset()
            scene.reset()
            last_reset_time = sim_time  # 마지막 리셋 시간 업데이트

        # [5] 로봇을 기본 자세로 고정
        targets = robot.data.default_joint_pos.clone()
        robot.set_joint_position_target(targets)
        robot.set_joint_velocity_target(torch.zeros_like(targets))

        # 데이터 기록 및 스텝 진행
        scene.write_data_to_sim()
        sim.step()
        
        # 장면 상태 업데이트 (최신 Z축 데이터를 가져오기 위해 필수)
        scene.update(dt=sim.get_physics_dt())

        # [6] 높이 측정 및 출력
        z_height = robot.data.root_pos_w[0, 2].item()
        z_height_cm = z_height * 100
        
        # 남은 시간 계산
        time_left = reset_interval - (sim_time - last_reset_time)

        # 실시간 상태 출력
        print(f"현재 높이: {z_height_cm:.2f} cm | 다음 리셋까지: {time_left:.1f}초    ", end="\r")

        # 시뮬레이션 시간 누적
        sim_time += sim.get_physics_dt()

    simulation_app.close()

if __name__ == "__main__":
    main()