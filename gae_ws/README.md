# 🐕 GAE Robot 통합 개발 환경 가이드 (v1.8)

> Docker 기반의 All-in-One 개발 환경입니다.
로컬에 복잡하게 라이브러리 설치할 필요 없이, 스크립트 하나로 개발을 시작하세요.
> 

---

## 🚀 빠른 시작 (Quick Start)

가장 먼저 `git pull`을 받아 최신 상태로 만들고, 아래 스크립트만 실행하세요.

### 1. 환경 실행

- 터미널에서 `gae_ws` 폴더로 이동 후 실행 스크립트를 가동합니다.
(이 스크립트가 USB, 카메라, GPU 권한을 모두 자동으로 연결합니다.)

```bash
cd ~/gae_ws

./run_gae.sh

colcon build --symlink-install

# build 에러 뜨면 아래 실행 후 다시 colcon build
# rm -rf build install log
# colcon build --symlink-install

source install/setup.bash
```

### 2. 빌드 (Container 내부)

- 도커 터미널(`root@ubuntu...`)이 열리면 바로 빌드

```python
# 전체 패키지 빌드
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

# 환경 변수 적용 (최초 1회 혹은 새 패키지 추가 시)
source install/setup.bash
```

## 3. 설치된 환경 요약 (v1.8)

이미지(`gae-system:v1.8`) 안에 아래 의존성들이 모두 세팅되어 있습니다. **따로 설치하지 마세요!**

- **시스템 및 코어 (System & Core)**

| **구분** | **패키지명** | **버전** | **설명 및 특이사항** |
| --- | --- | --- | --- |
| **OS** | Ubuntu | **22.04.3 LTS** | Jammy Jellyfish (Jetson Orin Nano 표준) |
| **ROS** | ROS 2 | **Humble** | Hawksbill (LTS 버전) |
| **CUDA** | CUDA Toolkit | **12.2** | V12.2.140 (GPU 가속을 위한 핵심 코어) |
| **Python** | Python | **3.10.12** | Ubuntu 22.04 기본 파이썬 환경 |
- **인공지능 및 딥러닝 (AI & Deep Learning)**
    - Jetson의 NPU/GPU를 최대한 활용하도록 **최적화된 버전**이 설치되어 있습니다.
    (⚠️ `pip install`로 함부로 덮어쓰지 마세요. GPU 가속이 풀릴 수 있습니다.)

| **패키지명** | **버전** | **설명 및 특이사항** |
| --- | --- | --- |
| **PyTorch** | **2.2.0** | **GPU 가속(CUDA) 활성화됨.** 모델 학습/추론의 핵심. |
| **TorchVision** | 0.17.2 | 이미지 처리용 라이브러리 (PyTorch 연동) |
| **Torch2TRT** | 0.5.0 | **⭐ 중요:** PyTorch 모델을 TensorRT로 변환해주는 툴. (추론 속도 3~5배 향상 가능) |
| **Ultralytics** | **8.4.9** | **YOLOv8** 공식 라이브러리. (객체 인식 구현 시 사용) |
| **faster-whisper** | **1.2.1** | **OpenAI Whisper**의 고속 추론 버전. (CTranslate2 기반 최적화) |
| **NumPy** | **1.26.4** | **⚠️ 중요:** PyTorch/OpenCV 호환성을 위해 **2.0 미만**으로 고정됨. |
- **비전 및 센서 (Vision & Sensors)**

| **패키지명** | **버전** | **설명 및 특이사항** |
| --- | --- | --- |
| **OpenCV** | **4.13.0** | **CUDA 가속 빌드.** (CPU 버전보다 이미지 처리 속도 월등히 빠름) |
| **astra_camera** | (Source) | **Orbbec Astra Pro 드라이버.** (`libuvc` 패치 적용하여 소스 빌드됨) |
| **camera_info_manager** | (Binary) | 카메라 캘리브레이션(.yaml) 로더.
**해상도 변경 시 필수.** |
| **rtabmap_ros** | (Binary) | RGB-D 카메라 기반 **VSLAM** 패키지 |
| **astra_camera_msgs** | (Source) | Astra 카메라 전용 메시지 타입 정의 |

- **음성 및 오디오 (Voice & Audio)**

| **패키지명** | **버전** | **설명 및 특이사항** |
| --- | --- | --- |
| **SpeechRecognition** | **3.14.5** | 오디오 입력 및 음성 인식 전처리 라이브러리 |
| **PyAudio** | **0.2.11** | 마이크 하드웨어 제어 및 입출력 담당 (PortAudio 기반) |
| **gTTS** | **2.5.4** | **Google Text-to-Speech.** 텍스트를 음성(mp3)으로 변환하는 라이브러리. |
| **pulseaudio-utils** | 15.99.1 | **시스템 오디오 도구.** `pactl` 명령어로 마이크/스피커 ID 확인 가능. |
| **SoX** | 14.4.2 | **오디오 처리 툴.** `play`, `rec` 명령어 포함 (mp3 재생 및 변환). |
| **libasound2-plugins** | (latest) | **ALSA-PulseAudio 브릿지.** 도커-호스트 간 오디오 스트리밍 최적화 |

- **하드웨어 제어 (Hardware Control)**

| **패키지명** | **버전** | **설명 및 특이사항** |
| --- | --- | --- |
| **adafruit-circuitpython-servokit** | 1.3.22 | **PCA9685** (16채널 PWM 드라이버) 제어용. **DS3218MG** 서보 구동 핵심 라이브러리. |
| **adafruit-circuitpython-mpu6050** | 1.3.5 | **MPU-6050** IMU 센서 데이터 수신용. Blinka 위에서 동작. |
| **libgpiod / python3-libgpiod** | (System) | **⭐ 최신 표준:** **HC-SR04P(초음파)** 제어를 위한 리눅스 표준 GPIO 도구. |
| **adafruit-blinka** | 8.23.0 | CircuitPython 라이브러리를 일반 리눅스 환경에서 쓰게 해주는 미들웨어. |
| **smbus2** | 0.6.0 | 저수준 I2C 통신 라이브러리. IMU 및 기타 I2C 장치 디버깅용. |

- **통신 및 인터페이스 (Communication & Interface)**

| **패키지명** | **버전** | **설명 및 특이사항** |
| --- | --- | --- |
| **paho-mqtt** | **2.1.0** | **MQTT 프로토콜** 클라이언트. 로봇(Pub)과 웹 서버(Sub) 간의 실시간 데이터 송수신 담당. |

## 4. 프로젝트 폴더 구조

```python
~/gae_ws/
│
├── 📂 docs/               # 회의록, 아키텍처 다이어그램, 이미지 등
├── 📄 README.md           # [메인] 프로젝트 설명서
├── 📄 requirements.txt    # [설정] 파이썬 패키지 명세서 (pip)
├── 📜 run_gae.sh          # [실행] 도커 컨테이너 시동 스크립트
├── 📜 update_env.sh       # [관리] 환경 동기화 스크립트
├── 🚫 .gitignore          # [Git] 불필요한 파일 무시 설정
│
└── 📂 src/                # [개발] 소스 코드 메인 디렉토리
    │
    ├── 🟢 [Team GAE 패키지] ----------------------------------
    │   │
    │   │
    │   ├── 📦 gae_bringup/     # [통합] 로봇 전체 실행 (.launch.py)
    │   │
    │   ├── 📦 gae_control/     # [제어] 강화학습(RL) 및 보행 알고리즘
    │   │   ├── 📂 config/      # 제어 파라미터 (.yaml)
    │   │   └── 📂 models/      # Isaac Sim 학습된 RL 정책 파일 (.onnx/.pt)
    │   │
    │   ├── 📦 gae_hardware/    # [하드웨어] PCA9685(서보), IMU 센서 드라이버
    │   │   └── 📂 config/      # 핀맵 및 캘리브레이션 설정
    │   │
    │   ├── 📦 gae_interface/   # [통신] 웹 서버 / 음성 인식(STT) / gTTS
    │   │
    │   ├── 📦 gae_msgs/        # [메시지] 커스텀 msg/srv 인터페이스 정의
    │   │
    │   └── 📦 gae_perception/  # [인식] YOLOv8, SLAM, OpenCV
    │       ├── 📂 config/      # 카메라/SLAM 설정 파일
    │       ├── 📂 launch/      # 인식 모듈 개별 실행 파일
    │       └── 📂 weights/     # YOLOv8 학습 가중치 파일 (.pt)
    │
    │
    └── 🔴 [외부 라이브러리 - 수정 주의] ------------------------
        │
        └── 📦 ros2_astra_camera/ # Orbbec Astra Pro 카메라 드라이버
            ├── astra_camera/
            └── astra_camera_msgs/
```

- **`ros2_astra_camera` (외부 드라이버)**
    - Orbbec 제조사에서 제공한 C++ 기반 드라이버를 Jetson 환경에 맞게 빌드해둔 것입니다.
    - 개발 중 **"카메라 실행 파일이 어딨지?"** 찾을 때만 아래 구조를 참고하세요.
    
    | **폴더명** | **설명 및 특이사항** |
    | --- | --- |
    | **`launch/`** | **[실행 파일 위치]** 
     ⚠️ **주의:** 여기는 Python(`.py`)이 아니라 **XML(`.xml`)** 형식을 씁니다.
     • **`astra_pro.launch.xml`** : ★ 우리가 사용할 유력한 실행 파일
     • `multi_astra.launch.xml` : 카메라 여러 대 쓸 때 참조 |
    | **`src/`** | **[소스 코드 (C++)]** 
     • `uvc_camera_driver.cpp` : RGB 카메라 제어 (libuvc 사용)
     • `ob_camera_node.cpp` : ROS 2 노드 메인
     *(건드리지 마세요. 빌드 꼬입니다.)* |
    | **`scripts/`** | **[설정 스크립트]** 
     • `56-orbbec-usb.rules` : USB 권한 설정 파일 (이미 적용됨) |
    - **카메라 실행 방법 (참고용)**
    
    ```python
    # 1. 패키지 이름: astra_camera
    # 2. 실행 파일: astra_pro.launch.xml (뒤에 .xml 꼭 붙이는 것 권장)
    
    # 도커 터미널1 에서 카메라 실행
    ros2 launch astra_camera astra_pro.launch.xml
    
    # 도커 터미널2 에서 토픽 발행 확인
    ros2 topic list
    /camera/color/camera_info
    /camera/color/image_raw
    /camera/depth/camera_info
    /camera/depth/image_raw
    /camera/depth/points
    /camera/ir/camera_info
    /camera/ir/image_raw
    /parameter_events
    /rosout
    /tf
    /tf_static
    
    # 도커 터미널2 에서 데이터가 진짜 들어오는지 주파수(Hz) 체크
    ros2 topic hz /camera/color/image_raw
    average rate: 28.068
            min: 0.031s max: 0.100s std dev: 0.01239s window: 29
    ```
    

## 5. 시스템 리소스 모니터링 (jtop)

- Jetson Orin Nano의 VRAM(8GB) 상태를 확인하고 싶다면 **호스트 터미널**에서 아래 명령어를 쓰세요.

```python
jtop
```

- **MEM:** 시스템 메모리 및 Swap 사용량 체크
- **GPU:** AI 모델 돌릴 때 부하 체크

## 6. 트러블슈팅

- 혹시 Orbbec 카메라가 인식이 안 된다면, USB를 뺐다 꽂은 후 **호스트**에서 아래 명령어를 한 번 입력해 주세요. (Udev 규칙 리로드)

```python
sudo udevadm control --reload-rules && sudo udevadm trigger
```

- 도커 컨테이너는 관리자만이 파일을 편집할 수 있도록 권한을 뺏음. 해당 명령어로 ~/gae_ws/src 아래 폴더 대한 권한 가져오기

```python
ssafy@ubuntu:~/gae_ws/src$ sudo chown -R ssafy:ssafy ~/gae_ws/src
```

## 7. 협업 컨벤션(규칙)

- **ROS 2 네이밍 컨벤션 (Naming)**
    - Python 코드
        - **클래스명:** `PascalCase` (예: `GaePerceptionNode`)
        - **함수/변수명:** `snake_case` (예: `detect_object`, `image_raw`)
    - ROS 토픽 & 노드 이름
        
        
        | **구분** | **규칙** | **예시** |
        | --- | --- | --- |
        | **노드 이름** | 기능_node | `perception_node`, `control_node` |
        | **토픽 이름** | /gae/대분류/데이터 | `/gae/camera/rgb/image_raw`
        `/gae/control/cmd_vel` |
        | **서비스 이름** | /gae/대분류/동사 | `/gae/system/reset_motor` |
- **파일 및 폴더 위치 규칙**
    - **실행 파일(.launch.py):** 무조건 `gae_bringup` 패키지에 통합하거나, 각 패키지의 `launch/` 폴더에.
    - **설정 값(.yaml):** 각 패키지의 `config/` 폴더. (코드 안에 하드코딩 금지 🚫)
    - **모델 파일(.pt, .onnx):**
        - `gae_perception/weights/`
        - `gae_control/models/`
    - **package.xml:** 새로운 라이브러리를 쓸 때마다 반드시 고쳐야 합니다
        - **수정 시점:**
            1. **커스텀 메시지 사용 시:** 우리가 만든 `gae_msgs`를 다른 패키지에서 쓸 때.
            2. **다른 ROS 패키지 의존 시:** `sensor_msgs`나 `cv_bridge` 같은 표준 패키지를 쓸 때.
        - `import` 하는 ROS 패키지나 커스텀 메시지는 반드시 `package.xml`의 `<depend>` 태그에 명시
            
            ```python
            ``특정 ros2 패키지의 package.xml``
            <depend>rclpy</depend>
            <depend>gae_msgs</depend> <depend>sensor_msgs</depend> <depend>cv_bridge</depend>
            
            ```
            
            - gae_msgs는 우리가 만든 커스텀 메시지, sensor_msgs, cv_bridge는 표준 패키므로 추가
    - **!!경로!!**
        - **"절대 경로(`/home/ssafy/...`)는 독약입니다."**
            - 팀원 누구의 컴퓨터에서든, 어떤 경로에 폴더를 두든 돌아가게 하려면 **ROS 2 표준 경로 관리 방식**을 써야 합니다.
        - **ROS 2 패키지 상대 경로 사용**
            - `get_package_share_directory` 함수를 사용하여 패키지가 설치된 위치를 기준으로 파일을 찾게 합니다.
            
            ```python
            # 예시
            import os
            from ament_index_python.packages import get_package_share_directory
            
            # 패키지의 설치 경로(install 폴더 안)를 자동으로 찾아줌
            package_share_directory = get_package_share_directory('gae_perception')
            
            # 그 안에서 weights/폴더 안의 파일을 지정
            model_path = os.path.join(package_share_directory, 'weights', 'yolov8n.pt')
            ```
            
    - **설정 파일(`launch`, `config`, `models` 등)을 새로 추가**했다면, **반드시 `setup.py`에도 등록**해야 빌드된다.
- **git 규칙**
    - 현재 `~/gae_ws/src` 폴더는 **Jetson(호스트)과 Docker(컨테이너)가 서로 "공유"**하고 있습니다.
        - 도커 안에서 파일을 수정해도 → 바깥(Jetson)에 저장됩니다.
        - 바깥(Jetson)에서 파일을 수정해도 → 안(Docker)에 반영됩니다
    - **Git 명령(add, commit, push)은** 굳이 도커 안에서 할 필요 없이, **바깥(Jetson 호스트 터미널)에서 하는 게 훨씬 편하고 안전**
    - **~/gae_ws/src 에서 git 저장소 연결 후 commit - push 진행하면 됩니다.**