from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'gae_perception'

setup(
    name=package_name,
    version='0.0.0',
    # 1. 중요: config 폴더를 패키지로 포함시키기 위해 find_packages가 필요합니다.
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        # Launch 파일
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        
        # Maps 
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
        
        # Config (여기에 .py 파일이 있어도 상관없지만, 실행을 위해선 entry_points가 핵심입니다)
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        
        # weights 
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
            # 파일이 gae_perception/config/depth_to_web.py에 있다면:
            'depth_converter = gae_perception.depth_to_web:main',
        ],
    },
) 