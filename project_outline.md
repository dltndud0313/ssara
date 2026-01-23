# 사용하고 싶은 기술 스택

> 글머리 번호 최상위 항목은 `사용하고 싶은 기술 스택의 이름`이고, 차상위 항목은 `실제 사용처`입니다. `태그` 양식은 `역할 분담 시 큰 카테고리`정도로 생각하면 될 것 같습니다. 태그가 없는 영역은 로봇 영역입니다.
>
> > `AD(Autonomous driving)` = 자율주행

1. NVIDIA Issac ROS, Issac Sim, Issac lab
   - `AD` Issac Sim을 통한 실제 시연 전 시뮬레이션
   - `AD` Isaac Sim + Issac lab을 통한 로봇 강화학습(RL) 데이터 확보
   - VLA, Physical AI
2. ROS2
   - `AD` ROS2 Humble + ubuntu 22.04
3. RGB카메라만을 활용한 자율 주행
   - `AD` Stereo Vision을 통한 Depth 데이터 확보(필요성 조사 필요)
   - `AI` 모델 import, 필요하다면 학습을 통해 객체인식
   - `AD + AI`**최종적으로 depth 카메라와 Lidar 센서를 사용하지 않고, 장애물을 회피하며 목표물을 찾아가는 자율주행 구현**
4. 마이크를 활용한 음성인식 AI로 명령 전달
5. 하드웨어 모델링 및 제작(3D프린팅, 선반가공, 레이저가공 등)
   - `HW` 카메라 거치대 모델링 및 프린팅(카메라 음영 영역 및 미관을 고려한 설계 반영)
6. `HW` PCB 설계 및 최종본 인쇄
7. `Web`동일 네트워크 상이 아닌 외부 네트워크를 통한 로봇 IOT 제어
   - 담당자 기획 추가
   - 모니터링

# Hardware

## BOM

[spot Micro BOM](https://docs.google.com/spreadsheets/d/18mxItY0H7ypNeKVTIqvK2lVw06e1zQXP21BfDEnFfvg/edit?gid=450530006#gid=450530006)

# 더 조사해 봐야 할 기술
1. Physical AI
2. VLA
3. CES 보고 아이디어 찾아보기
4. walk
5. object detection
6. vslam
   1. real world

앞부분은 제 생각에 포트폴리오에 작성 시 유용할 만한 기술 스택들을 정리한 내용이고, 뒷부분은 이 기술 스택들을 활용한 프로젝트 예시입니다.

# 임시 메모

Isaac 초기 + 학습 과정 전체적으로 보여주기 - 개발 과정을 스크린 샷, 스크린 레코드로 꾸준히 기록 해두기
jira 30 + git 30 + pjt 40, agile??, git flow vs github flow vs gitlab flow??
