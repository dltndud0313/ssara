#!/bin/bash
# 시각화 권한 부여
xhost +local:root > /dev/null

# 내 컨테이너 이름 (jjy092801)으로 접속
docker exec -it jjy092801 /bin/bash