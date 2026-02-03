#!/bin/bash

# 1. 현재 호스트의 유저 이름을 가져옵니다. (jjy092801, taeyeon, sooyoung 등)
# 만약 호스트 계정명과 컨테이너 이름이 같다면 그대로 사용합니다.
CURRENT_USER=$(whoami)

# 2. 예외 처리: 정지용 님 호스트 계정명이 jjy092801이 아니라면? 
# 혹은 특정 환경변수를 쓰고 싶다면 여기서 분기 처리를 합니다.
if [ "$CURRENT_USER" == "ssafy" ]; then
    # 만약 공용 계정(ssafy)을 쓴다면, 누가 접속했는지 알 수 있게 환경변수를 쓰거나 선택하게 해야 합니다.
    echo "Current user is 'ssafy'. Please select your container name:"
    # 여기서는 예시로 jjy092801를 기본값으로 둡니다.
    CONTAINER_NAME=${GAE_CONTAINER:-jjy092801}
else
    # 호스트 계정명과 컨테이너 이름을 일치시켜놨다면 이게 제일 깔끔합니다.
    CONTAINER_NAME=${GAE_CONTAINER:-$CURRENT_USER}
fi

# X11 시각화 권한
if [ -n "$DISPLAY" ]; then
  xhost +local:root > /dev/null
fi

# 호스트 PulseAudio 체크
if ! pactl info >/dev/null 2>&1; then
  echo "[WARN] PulseAudio server not reachable on host."
  echo "        run: pulseaudio --start"
fi

echo "Connecting to container: $CONTAINER_NAME..."
docker exec -it "$CONTAINER_NAME" /bin/bash