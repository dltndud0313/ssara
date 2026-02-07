#!/bin/bash

# 1. 컨테이너 이름을 본인 ID로 강제 고정
CONTAINER_NAME="jjy092801"

# 2. X11 시각화 권한 (Isaac Sim이나 GUI 띄울 때 필요)
if [ -n "$DISPLAY" ]; then
  xhost +local:root > /dev/null
fi

# 3. 호스트 PulseAudio 체크 (오디오 필요 시)
if ! pactl info >/dev/null 2>&1; then
  echo "[WARN] PulseAudio server not reachable on host."
  echo "        run: pulseaudio --start"
fi

echo "Connecting to container: $CONTAINER_NAME..."

# 4. Docker 컨테이너 접속
docker exec -it "$CONTAINER_NAME" /bin/bash