#!/bin/bash

# 컨테이너 이름 (환경변수 or 기본값)
CONTAINER_NAME=${GAE_CONTAINER:-gae_master}

# X11 시각화 권한 (DISPLAY 있을 때만)
if [ -n "$DISPLAY" ]; then
  xhost +local:root > /dev/null
fi

# 호스트 PulseAudio 체크
if ! pactl info >/dev/null 2>&1; then
  echo "[WARN] PulseAudio server not reachable on host."
  echo "       run: pulseaudio --start"
fi

docker exec -it "$CONTAINER_NAME" /bin/bash