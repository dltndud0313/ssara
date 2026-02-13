# Project Overview
## 로봇 flow
- Isaac Lab을 통한 평지/험지보행 강화 학습
  - import Assembly(onshape) to URDF to USD
  - cfg 파일 설정하기
    - 강화학습 보상 설정
    - 기타 등등,,,
  - 위에서 정의한 환경, 보상으로 강화학습 진행
  - 강화학습 결과로 생성된 policy(.onyx)를 로봇 SBC에 Upload !! 이 부분 controlled_by_model.py에 링크
    - 이번에 사용한 모델에 대해 간단히 요약하자면, 50hz로 신호를 주고 받는데 12개(각 관절마다 3개씩)의 조인트 각도 값 history 5개, 즉 1/50*5=0.1초 동안의 데이터와 6개의 IMU 데이터를 받아서, 같은 주파수로 12개의 액츄에이터에 신호를 쏘는 모델이라 할 수 있다.
    - 체크포인트마다 .pt 파일이 생성되고, 실제 시뮬레이션 결과 확인 시에는 이 파일을 사용
    - 실제 로봇 SBC에 업로드 시에는 .onyx 파일 사용

## Web flow

## Other functions impl flow

## 