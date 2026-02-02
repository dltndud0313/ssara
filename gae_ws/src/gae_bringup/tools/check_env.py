#!/usr/bin/env python3
import sys
import subprocess
import importlib

def check_python_package(package_name, import_name=None, expected_version=None):
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        # 패키지마다 버전 확인 변수가 다를 수 있음
        version = getattr(module, '__version__', getattr(module, 'VERSION', '설치됨 (버전 정보 없음)'))
        
        status = "✅ OK"
        if expected_version and expected_version not in version:
            status = f"⚠️ 버전 다름 ({version})"
            
        print(f"[{status}] {package_name:<30} : {version}")
        return module
    except ImportError:
        print(f"[❌ MISSING] {package_name:<30} : 설치 안됨")
        return None

def check_ros_package(package_name):
    try:
        result = subprocess.run(['ros2', 'pkg', 'list'], capture_output=True, text=True)
        if package_name in result.stdout:
            print(f"[✅ OK] ROS Package: {package_name:<17} : 설치됨")
        else:
            print(f"[❌ MISSING] ROS Package: {package_name:<17} : 리스트에 없음")
    except Exception:
        print(f"[❌ ERROR] ROS 2 환경을 찾을 수 없음")

def run_system_check():
    print("="*60)
    print("🚀 GAE Robot 환경 진단 (v1.9 Final)")
    print("="*60)

    # 1. AI & Deep Learning
    print("\n---------- 1. AI & Deep Learning ----------")
    check_python_package("numpy", "numpy", "1.26.4")
    
    torch = check_python_package("torch", "torch", "2.2.0")
    if torch:
        cuda_ok = torch.cuda.is_available()
        print(f"   ㄴ CUDA 가속 활성화?           : {'✅ YES' if cuda_ok else '❌ NO (GPU 안 잡힘!)'}")
        if cuda_ok:
            print(f"   ㄴ 감지된 GPU 장치             : {torch.cuda.get_device_name(0)}")

    check_python_package("torchvision", "torchvision", "0.17")
    check_python_package("ultralytics", "ultralytics", "8.4.9")
    check_python_package("faster-whisper", "faster_whisper")
    check_python_package("torch2trt", "torch2trt")

    # 2. Vision & Sensors
    print("\n---------- 2. Vision & Sensors ----------")
    cv2 = check_python_package("opencv-python", "cv2", "4.13.0")
    if cv2:
        try:
            count = cv2.cuda.getCudaEnabledDeviceCount()
            print(f"   ㄴ OpenCV CUDA 가속?           : {'✅ YES' if count > 0 else '❌ NO (CPU 전용 - 성능저하 주의)'}")
        except:
            print(f"   ㄴ OpenCV CUDA 확인 불가")

    check_ros_package("astra_camera")
    check_ros_package("astra_camera_msgs")
    check_ros_package("rtabmap_ros")
    check_ros_package("camera_info_manager")
    check_ros_package("web_video_server")

    # 3. Audio & Control & Interface
    print("\n---------- 3. Audio / Hardware / Interface ----------")
    check_python_package("SpeechRecognition", "speech_recognition")
    check_python_package("PyAudio", "pyaudio")
    check_python_package("gTTS", "gtts")
    check_python_package("paho-mqtt", "paho.mqtt", "2.1.0")
    
    # 4. 하드웨어 제어 (Hardware Control)
    print("\n---------- 4. Hardware Control ----------")
    # Blinka 에러 방지용 필수 패키지 (Jetson.GPIO)
    check_python_package("Jetson.GPIO", "Jetson.GPIO") 
    
    check_python_package("adafruit-circuitpython-servokit", "adafruit_servokit")
    check_python_package("adafruit-circuitpython-mpu6050", "adafruit_mpu6050")
    check_python_package("adafruit-blinka", "adafruit_blinka")
    check_python_package("smbus2", "smbus2")

    # 5. System Tools
    print("\n---------- 5. System Tools ----------")
    tools = ["nvcc --version", "jtop --version", "sox --version"]
    
    # apt 패키지 확인
    apt_packages = ["pulseaudio-utils", "libasound2-plugins", "gpiod"]
    for pkg in apt_packages:
        res = subprocess.run(f"dpkg -s {pkg}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            print(f"[✅ OK] APT Package: {pkg:<17} : 설치됨")
        else:
            print(f"[❌ MISSING] APT Package: {pkg:<17} : 설치 안됨")

    for tool in tools:
        cmd = tool.split()[0]
        try:
            subprocess.run(tool.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"[✅ OK] Command: {cmd:<21} : 설치됨")
        except FileNotFoundError:
            print(f"[❌ MISSING] Command: {cmd:<21} : 명령어를 찾을 수 없음")

    print("="*60)
    print("진단 완료.")

if __name__ == "__main__":
    run_system_check()