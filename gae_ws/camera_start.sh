#!/bin/bash

# 종료(Ctrl+C) 시 켜진 프로그램들(카메라, SLAM 등) 한방에 끄기
trap 'kill $(jobs -p)' SIGINT

echo "🚀 [camera_start] 로봇 시스템 가동 시작..."

# 1. 환경 설정 (source)
# (root 사용자, gae_ws 경로에 맞춰 수정했습니다)
source /opt/ros/humble/setup.bash
source ~/gae_ws/install/setup.bash

# 2. [눈] 카메라 실행 (Astra Pro)
# (백그라운드 & 실행)
echo "📷 Astra Pro 카메라 켜는 중..."
ros2 launch astra_camera astra_pro.launch.xml &

# 3. [대기] 카메라가 연결될 때까지 5초 기다림 (필수!)
echo "⏳ 카메라 초기화 대기 (5초)..."
sleep 5

# 4. [뇌] SLAM 및 전체 시스템 실행
# (방금 알려주신 명령어를 여기에 넣었습니다)
echo "🧠 SLAM, AI, MQTT 통신 모듈 실행 중..."
ros2 launch gae_perception slam.launch.py

# 스크립트가 꺼지지 않게 대기
wait
