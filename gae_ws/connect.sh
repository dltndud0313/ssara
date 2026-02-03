#!/bin/bash
# 시각화 권한 부여
xhost +local:root > /dev/null

# 호스트 PulseAudio 서버 체크
if ! pactl info >/dev/null 2>&1; then
  echo "[WARN] PulseAudio server not reachable on host."
  echo "       run: pulseaudio --start"
fi

# 내 컨테이너 이름으로 접속
docker exec -it jjy092801 /bin/bash