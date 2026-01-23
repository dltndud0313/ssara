from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.objects import FixedCuboid
from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.prims import delete_prim, is_prim_path_valid
import omni.usd
import numpy as np

# ---------------------------------------------------------
# [설정] 맵 파일 경로
usd_path = "/workspace/IsaacLab/my_projects/spot_micro/simple_map.usd"

# [설정] 경기장 크기
MAP_WIDTH = 1.5
MAP_LENGTH = 2.5
WALL_HEIGHT = 0.3
THICKNESS = 0.02   # 벽 두께

# [설정] 보도(인도) 크기
SIDEWALK_WIDTH = 0.4  # 양옆 보도 폭 (40cm)
SIDEWALK_HEIGHT = 0.02 # 보도 턱 높이 (2cm)
# ---------------------------------------------------------

print(f"[INFO] Loading USD file: {usd_path}")
omni.usd.get_context().open_stage(usd_path)

world = World()

# 1. 청소 (기존 것들이 있으면 삭제)
prims_to_delete = [
    "/World/GroundPlane", "/World/ArenaFloor", "/World/RedPillar",
    "/World/Wall_Left", "/World/Wall_Right", "/World/Wall_Top", "/World/Wall_Bottom",
    "/World/Sidewalk_Left", "/World/Sidewalk_Right", "/World/ObstacleBox"
]
for prim in prims_to_delete:
    if is_prim_path_valid(prim):
        delete_prim(prim)

# 2. 바닥 = 아스팔트 도로 (검은색)
world.scene.add(
    FixedCuboid(
        prim_path="/World/RoadFloor",
        name="road_floor",
        position=np.array([0, 0, -0.05]),
        scale=np.array([MAP_WIDTH, MAP_LENGTH, 0.1]),
        color=np.array([0.15, 0.15, 0.15]) # 진한 회색
    )
)

# 3. 보도 블럭 (붉은색) - 양옆
world.scene.add(
    FixedCuboid(
        prim_path="/World/Sidewalk_Left",
        name="sidewalk_left",
        position=np.array([-(MAP_WIDTH/2 - SIDEWALK_WIDTH/2), 0, SIDEWALK_HEIGHT/2]),
        scale=np.array([SIDEWALK_WIDTH, MAP_LENGTH, SIDEWALK_HEIGHT]),
        color=np.array([0.6, 0.3, 0.2])
    )
)

world.scene.add(
    FixedCuboid(
        prim_path="/World/Sidewalk_Right",
        name="sidewalk_right",
        position=np.array([(MAP_WIDTH/2 - SIDEWALK_WIDTH/2), 0, SIDEWALK_HEIGHT/2]),
        scale=np.array([SIDEWALK_WIDTH, MAP_LENGTH, SIDEWALK_HEIGHT]),
        color=np.array([0.6, 0.3, 0.2])
    )
)

# 4. 횡단보도 (흰색 줄무늬)
for i in range(3):
    world.scene.add(
        FixedCuboid(
            prim_path=f"/World/Crosswalk_{i}",
            name=f"crosswalk_{i}",
            position=np.array([0, 0.5 + (i * 0.2), 0.001]),
            scale=np.array([0.6, 0.1, 0.001]),
            color=np.array([0.9, 0.9, 0.9])
        )
    )

# 5. 벽 세우기 (이름 충돌 해결됨!)
z_pos = WALL_HEIGHT / 2
x_offset = (MAP_WIDTH / 2) + (THICKNESS / 2)
y_offset = (MAP_LENGTH / 2) + (THICKNESS / 2)

# 좌우 벽 (name에 _obj 추가해서 충돌 방지)
world.scene.add(FixedCuboid(prim_path="/World/Wall_Left", name="wall_left_obj", position=np.array([-x_offset, 0, z_pos]), scale=np.array([THICKNESS, MAP_LENGTH, WALL_HEIGHT]), color=np.array([0.1, 0.1, 0.1])))
world.scene.add(FixedCuboid(prim_path="/World/Wall_Right", name="wall_right_obj", position=np.array([x_offset, 0, z_pos]), scale=np.array([THICKNESS, MAP_LENGTH, WALL_HEIGHT]), color=np.array([0.1, 0.1, 0.1])))

# 상하 벽
world.scene.add(FixedCuboid(prim_path="/World/Wall_Top", name="wall_top_obj", position=np.array([0, y_offset, z_pos]), scale=np.array([MAP_WIDTH + THICKNESS*2, THICKNESS, WALL_HEIGHT]), color=np.array([0.1, 0.1, 0.1])))
world.scene.add(FixedCuboid(prim_path="/World/Wall_Bottom", name="wall_bottom_obj", position=np.array([0, -y_offset, z_pos]), scale=np.array([MAP_WIDTH + THICKNESS*2, THICKNESS, WALL_HEIGHT]), color=np.array([0.1, 0.1, 0.1])))

# 6. 장애물 & 로봇
world.scene.add(
    FixedCuboid(
        prim_path="/World/ObstacleBox",
        name="obstacle_box",
        position=np.array([(MAP_WIDTH/2 - SIDEWALK_WIDTH/2), 0.5, 0.15 + SIDEWALK_HEIGHT]),
        scale=np.array([0.2, 0.2, 0.3]),
        color=np.array([0.9, 0.9, 0.9])
    )
)

robot = Articulation(prim_path="/World/SpotMicroAI", name="my_spot")
world.scene.add(robot)
robot.set_world_pose(position=np.array([0, -0.5, 0.2]))

world.reset()
print(f"[INFO] Road Arena Created Successfully!")

while simulation_app.is_running():
    world.step(render=True)

simulation_app.close()