#!/bin/bash

# X11 권한 (시각화용)
xhost +local:root

# 이미지 이름 변수로 관리 (나중에 버전 바뀌면 여기만 고치면 됨)
# 👇 여기에 본인 아이디가 들어간 새 이미지를 적습니다.
DOCKER_IMAGE="jjy092801/gae-system:v2.0"

echo "🚀 Ros2 시스템 가동: $DOCKER_IMAGE"

docker run -it --rm \
    --runtime nvidia \
    --network host \
    --privileged \
    -v /dev:/dev \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /run/jtop.sock:/run/jtop.sock \
    -v $(pwd):/root/gae_ws \
    -w /root/gae_ws \
    -e DISPLAY=$DISPLAY \
    -e QT_X11_NO_MITSHM=1 \
    $DOCKER_IMAGE
