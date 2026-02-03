import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Astra Pro 카메라 패키지 경로
    astra_pkg = get_package_share_directory('astra_camera')
    rtabmap_pkg = get_package_share_directory('rtabmap_launch')

    # 2. 카메라 실행 (RGB-D 모드)
    # FPS를 15로 낮춰서 데이터 전송량과 CPU 부하를 줄임 -> 동기화 성공률 상승
    camera_launch = IncludeLaunchDescription(
        XMLLaunchDescriptionSource(
            os.path.join(astra_pkg, 'launch', 'astra_pro.launch.xml')
        ),
        launch_arguments={
            'color_fps': '30',
            'depth_fps': '30',
            'ir_fps': '30',
	    'color_width': '320',  
            'color_height': '240', 
            'depth_width': '320',  
            'depth_height': '240'
	
        }.items()
    )

    # 3. RTAB-Map 실행 (SLAM 메인)
    rtabmap_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(rtabmap_pkg, 'launch', 'rtabmap.launch.py')
        ),
        launch_arguments={
            'rtabmap_args': '--delete_db_on_start '        # 시작 시 이전 맵 삭제
                            '--Mem/Strategy 1 '            # 작업 메모리 전략
                            '--Mem/IncrementalMemory True '
                            '--Grid/FromDepth True '       # 깊이 영상으로 2D 점유 지도 생성
                            '--Reg/Force3DoF True',        # 평지 이동 로봇(3DoF) 모드
            'frame_id': 'base_link',
            'subscribe_depth': 'true',
            'subscribe_rgb': 'true',
            'approx_sync': 'true',            # 중요: 타임스탬프가 완벽히 같지 않아도 허용
            'approx_sync_max_interval': '0.05', # 중요: 허용 오차를 0.05초(50ms)로 넉넉하게 설정
            'rgb_topic': '/camera/color/image_raw',
            'depth_topic': '/camera/depth/image_raw',
            'camera_info_topic': '/camera/color/camera_info',
            'qos': '2',                       # Best Effort 통신
            'rviz': 'false',                  # 리소스 절약
            'rtabmap_viz': 'false',           # 리소스 절약
        }.items()
    )
    
    # 4. TF (좌표계) 설정
    # static_transform_publisher arguments 순서: [X, Y, Z, Yaw, Pitch, Roll, 부모프레임, 자식프레임]
    # 단위: 미터(m), 라디안(rad)
    
    # [실제 로봇 적용 시 측정 방법]
    # 기준점(base_link): 로봇 몸통의 정중앙 (다리 제외, 몸체 박스의 가운데)
    # 목표점(camera_link): 카메라의 렌즈 중심
    
    # 1. X (앞/뒤): 로봇 몸통 중앙에서 카메라 렌즈가 앞으로 얼마나 튀어나왔는가? 
    #    (앞으로 나왔으면 양수, 뒤로 들어갔으면 음수. 예: 10cm 앞 -> '0.1')
    # 2. Y (좌/우): 로봇 몸통 중앙에서 카메라가 왼쪽/오른쪽으로 치우쳤는가?
    #    (정중앙에 달았으면 '0', 왼쪽이면 양수)
    # 3. Z (위/아래): 로봇 '바닥'이 아니라 '몸통 중앙' 높이에서 카메라가 얼마나 위에 있는가?
    #    (예: 몸통 두께의 절반 위 + 마운트 높이. 보통 5~10cm 위 -> '0.05' ~ '0.1')
    
    # 4. TF 설정
    tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0.1', '0', '0.1', '0', '0', '0', 'base_link', 'camera_link']
    )

    # 5. 뎁스 변환기 노드
    depth_to_web_node = Node(
        package='gae_perception',
        executable='depth_converter',
        name='depth_converter',
        output='screen'
    )

    # 6. 웹 서버 노드
    web_server_node = Node(
        package='web_video_server',
        executable='web_video_server',
        name='web_server',
        output='screen'
    )

    # 7. 실행 리스트 (콤마와 괄호를 꼭 확인하세요!)
    return LaunchDescription([
        tf_node,
        camera_launch,
        rtabmap_launch,
        depth_to_web_node,
        web_server_node
    ])
