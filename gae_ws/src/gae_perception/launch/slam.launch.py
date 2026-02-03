import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

def generate_launch_description():
    # 1. 패키지 및 환경 경로 자동 계산
    # get_package_share_directory는 'install' 폴더를 가리킴
    pkg_share = get_package_share_directory('gae_perception')
    astra_pkg = get_package_share_directory('astra_camera')
    rtabmap_pkg = get_package_share_directory('rtabmap_launch')

    # 2. [범용성 설정] 사용자 이름을 자동으로 감지하여 src 폴더 경로 설정
    # os.path.expanduser('~')를 쓰면 /home/ssafy 혹은 /home/sooyoung 등을 자동으로 잡습니다.
    home_dir = os.path.expanduser('~')
    
    # 팀 프로젝트 표준 경로 설정 (src 폴더에 직접 저장하여 협업 효율 극대화)
    # 아래 경로는 프로젝트 루트 폴더 이름이 'S14P11C101'일 경우를 가정합니다.
    workspace_root = os.path.join(home_dir, 'workspaces', 'sooyoung', 'S14P11C101')
    map_save_dir = os.path.join(workspace_root, 'src', 'gae_perception', 'maps')
    database_file = os.path.join(map_save_dir, 'rtabmap.db')

    # 만약 maps 폴더가 없으면 자동으로 생성 (에러 방지)
    if not os.path.exists(map_save_dir):
        os.makedirs(map_save_dir, exist_ok=True)

    # 3. 카메라 실행 (Astra Pro)
    # 웹 실시간 스트리밍(30fps)과 vSLAM 연산 효율을 모두 고려한 설정
    camera_launch = IncludeLaunchDescription(
        XMLLaunchDescriptionSource(
            os.path.join(astra_pkg, 'launch', 'astra_pro.launch.xml')
        ),
        launch_arguments={
            'color_fps': '30',
            'depth_fps': '30',
            'color_width': '320',  
            'color_height': '240', 
            'depth_width': '320',  
            'depth_height': '240'
        }.items()
    )

    # 4. RTAB-Map SLAM 실행
    rtabmap_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(rtabmap_pkg, 'launch', 'rtabmap.launch.py')
        ),
        launch_arguments={
            # [DB 경로 가로채기] install이 아닌 src/maps 폴더에 직접 기록
            'database_path': database_file,
            
            'rtabmap_args': '--delete_db_on_start '        # 실행 시 이전 맵 초기화 (새 맵핑 시 필수)
                            '--Rtabmap/DetectionRate 1 '  # 30fps 중 1fps만 연산하여 제슨 나노 부하 방지
                            '--Mem/Strategy 1 '            # 메모리 최적화
                            '--Grid/FromDepth True '       # 2D 점유 지도 생성 활성화
                            '--Reg/Force3DoF True',        # 4족 보행 로봇의 평면 주행 보정
            
            'frame_id': 'base_link',
            'subscribe_depth': 'true',
            'subscribe_rgb': 'true',
            'approx_sync': 'true',            # RGB-D 타임스탬프 허용 오차 활성화
            'approx_sync_max_interval': '0.05', 
            'rgb_topic': '/camera/color/image_raw',
            'depth_topic': '/camera/depth/image_raw',
            'camera_info_topic': '/camera/color/camera_info',
            'qos': '2',                       
            'rviz': 'false',                  
            'rtabmap_viz': 'false'            
        }.items()
    )
    
    # 5. 정적 좌표 변환 (TF: 로봇 중심 -> 카메라 렌즈)
    tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0.1', '0', '0.1', '0', '0', '0', 'base_link', 'camera_link']
    )

    # 6. 웹 모니터링 노드 (Depth 변환 + 스트리밍 서버)
    depth_to_web_node = Node(
        package='gae_perception',
        executable='depth_converter',  # <--- setup.py의 entry_points에 적은 이름과 일치해야 함!
        name='depth_converter',
        output='screen'
    )

    web_server_node = Node(
        package='web_video_server',
        executable='web_video_server',
        name='web_server'
    )

    return LaunchDescription([
        tf_node,
        camera_launch,
        rtabmap_launch,
        depth_to_web_node,
        web_server_node
    ])