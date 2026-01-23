from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.objects import FixedCuboid
from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.prims import delete_prim
import omni.usd
import numpy as np

# ---------------------------------------------------------
# [핵심] 아까 성공했던 "로봇 있는 맵" 파일 경로!
usd_path = "/workspace/IsaacLab/my_projects/spot_micro/simple_map.usd"
# ---------------------------------------------------------

print(f"[INFO] Loading USD file: {usd_path}")
omni.usd.get_context().open_stage(usd_path)

world = World()

# 1. 기존 바닥(GroundPlane) 철거하기
# (기존 무한 바닥을 지워야 경기장이 잘 보입니다)
print("[INFO] Deleting old ground plane...")
delete_prim("/World/GroundPlane")

# 2. 새로운 1.5m x 2.5m 경기장 바닥 깔기
# position z=-0.05 : 바닥 두께가 10cm라 절반만큼 내려야 윗면이 0이 됨
world.scene.add(
    FixedCuboid(
        prim_path="/World/ArenaFloor",
        name="arena_floor",
        position=np.array([0, 0, -0.05]),
        scale=np.array([1.5, 2.5, 0.1]),  # 가로 1.5m, 세로 2.5m
        color=np.array([0.2, 0.2, 0.2])   # 진한 회색
    )
)

# 3. 빨간 기둥(장애물) 심기
world.scene.add(
    FixedCuboid(
        prim_path="/World/RedPillar",
        name="red_pillar",
        position=np.array([0.5, 0.5, 0.15]), # 로봇 앞쪽 대각선 위치
        scale=np.array([0.2, 0.2, 0.3]),
        color=np.array([0.8, 0.2, 0.2])      # 빨간색
    )
)

# 4. 이미 있는 로봇 찾아서 등록하기
# (새로 불러오는 게 아니라, 파일에 있는 걸 찾아내는 겁니다)
robot = Articulation(prim_path="/World/SpotMicroAI", name="my_spot")
world.scene.add(robot)

# 로봇 위치 초기화 (경기장 중앙)
robot.set_world_pose(position=np.array([0, 0, 0.2]))

world.reset()
print("[INFO] Arena construction complete! Robot is ready.")

while simulation_app.is_running():
    world.step(render=True)

simulation_app.close()