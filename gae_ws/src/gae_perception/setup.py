from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'gae_perception'

setup(
    name=package_name,
    version='0.0.0',
    # 패키지 내의 모든 파이썬 모듈을 자동으로 찾습니다.
    packages=find_packages(exclude=['test']),
    data_files=[
        # 패키지 등록을 위한 리소스 파일
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        
        # Launch 파일 설치 (launch 폴더 내의 모든 .launch.py 파일)
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        
        # Map 파일 설치 (maps 폴더 내의 모든 파일)
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
        
        # Config 파일 설치 (config 폴더 내의 모든 파일)
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        
        # Weights 파일 설치 (YOLO 가중치 등)
        (os.path.join('share', package_name, 'weights'), glob('weights/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ssafy',
    maintainer_email='ssafy@todo.todo',
    description='GAE Robot Perception Package',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # [형식] '실행명령어 = 패키지명.파일명:함수명'
            
            # 1. 깊이 영상 변환 노드
            'depth_converter = gae_perception.depth_to_web:main',
            
            # 2. 판단 제어 노드
            'decision_node = gae_perception.decision_node:main',
            
            # 3. 객체 인식 노드
            'inference_node = gae_perception.inference_node:main',

            # 4. [추가됨] 위치 정보 MQTT 통신 브릿지
            'pose_bridge = gae_perception.pose_bridge:main',
        ],
    },
)