from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='rqt_image_view',
            executable='rqt_image_view',
            name='gae_rgb_viewer',
            # 가이드 규칙: 기본 토픽을 명시적으로 연결
            remappings=[('/image', '/camera/color/image_raw')]
        )
    ])
