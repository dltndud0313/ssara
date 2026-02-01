from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'gae_hardware'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        # Config (핀맵, I2C 주소 등 하드웨어 설정)
        (os.path.join('share', package_name, 'config'), glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ssafy',
    maintainer_email='ssafy@todo.todo',
    description='GAE Robot Hardware Control Package',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # 나중에 모터 제어 노드 같은 거 생기면 여기에 추가
            # 'motor_driver = gae_hardware.motor_driver:main',
        ],
    },
)