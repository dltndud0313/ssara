from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.objects import FixedCuboid
from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.prims import delete_prim
import omni.usd
import numpy as np

# ---------------------------------------------------------
# [설정] 맵 파일 경로
usd_path = "/workspace/IsaacLab/my_projects/spot_micro/simple_map.usd"

# [설정] 경기장 수치
MAP_WIDTH = 1.5    # 바닥 가로
MAP_LENGTH = 2.5   # 바닥 세로
WALL_HEIGHT = 0.3  # 벽 높이 (30cm)
THICKNESS = 0.02   # 벽 두께 (2cm)
# ---------------------------------------------------------

print(f"[INFO] Loading USD file: {usd_path}")
omni.usd.get_context().open_stage(usd_path)

world = World()

# 1. 기존 지저분한 벽들 청소
delete_prim("/World/GroundPlane")
delete_prim("/World/ArenaFloor")
delete_prim("/World/RedPillar")
delete_prim("/World/Wall_Left")
delete_prim("/World/Wall_Right")
delete_prim("/World/Wall_Top")
delete_prim("/World/Wall_Bottom")

# 2. 바닥 깔기
world.scene.add(
    FixedCuboid(
        prim_path="/World/ArenaFloor",
        name="arena_floor",
        position=np.array([0, 0, -0.05]),
        scale=np.array([MAP_WIDTH, MAP_LENGTH, 0.1]),
        color=np.array([0.3, 0.3, 0.3])
    )
)

# 3. 벽 세우기 (칼각 맞춤 전략!)
# 벽의 높이 중심 = 0.15 (바닥 0 위로 올라옴)
z_pos = WALL_HEIGHT / 2

# (1) 왼쪽/오른쪽 벽: 길이를 바닥과 똑같이(2.5m) 함 -> 위아래가 뚫려 있음
side_wall_length = MAP_LENGTH
x_offset = (MAP_WIDTH / 2) + (THICKNESS / 2)

# 왼쪽 벽
world.scene.add(
    FixedCuboid(
        prim_path="/World/Wall_Left",
        name="wall_left",
        position=np.array([-x_offset, 0, z_pos]),
        scale=np.array([THICKNESS, side_wall_length, WALL_HEIGHT]),
        color=np.array([0.6, 0.6, 0.6])
    )
)

# 오른쪽 벽
world.scene.add(
    FixedCuboid(
        prim_path="/World/Wall_Right",
        name="wall_right",
        position=np.array([x_offset, 0, z_pos]),
        scale=np.array([THICKNESS, side_wall_length, WALL_HEIGHT]),
        color=np.array([0.6, 0.6, 0.6])
    )
)

# (2) 위/아래 벽: 길이를 '바닥 폭 + 양쪽 벽 두께'로 늘려서 덮어버림 -> 모서리 마감
top_bottom_length = MAP_WIDTH + (THICKNESS * 2)
y_offset = (MAP_LENGTH / 2) + (THICKNESS / 2)

# 위쪽 벽
world.scene.add(
    FixedCuboid(
        prim_path="/World/Wall_Top",
        name="wall_top",
        position=np.array([0, y_offset, z_pos]),
        scale=np.array([top_bottom_length, THICKNESS, WALL_HEIGHT]),
        color=np.array([0.6, 0.6, 0.6])
    )
)

# 아래쪽 벽
world.scene.add(
    FixedCuboid(
        prim_path="/World/Wall_Bottom",
        name="wall_bottom",
        position=np.array([0, -y_offset, z_pos]),
        scale=np.array([top_bottom_length, THICKNESS, WALL_HEIGHT]),
        color=np.array([0.6, 0.6, 0.6])
    )
)

# 4. 장애물 & 로봇
world.scene.add(
    FixedCuboid(
        prim_path="/World/RedPillar",
        name="red_pillar",
        position=np.array([0.5, 0.5, 0.15]),
        scale=np.array([0.2, 0.2, 0.3]),
        color=np.array([0.8, 0.2, 0.2])
    )
)

robot = Articulation(prim_path="/World/SpotMicroAI", name="my_spot")
world.scene.add(robot)
robot.set_world_pose(position=np.array([0, 0, 0.25]))

world.reset()
print(f"[INFO] Perfect Corner Arena Created!")

while simulation_app.is_running():
    world.step(render=True)

simulation_app.close()