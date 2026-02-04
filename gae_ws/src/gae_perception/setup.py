from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'gae_perception'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        # Launch 파일
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        
        # Config (기본 설정 파일들)
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'config'), glob('config/*.rviz')),
        # map
        (os.path.join('share', package_name, 'config/maps'), glob('config/maps/*')),
        
        # weights (YOLO 모델 등)
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
		'depth_converter = gae_perception.depth_to_web:main',
        'data_recorder = gae_perception.data_recorder:main',
        ],
    },
)
