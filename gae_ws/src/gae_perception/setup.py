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
        # Launch 파일이 있다면 (나중에 launch 폴더 생기면 주석 해제)
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        
        # Config
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        
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
        ],
    },
)