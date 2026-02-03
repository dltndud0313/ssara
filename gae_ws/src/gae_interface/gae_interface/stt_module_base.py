import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import threading
import speech_recognition as sr
from faster_whisper import WhisperModel
from gtts import gTTS
import os
import io
import wave
import re

class VoiceAssistant:
    def __init__(self, mp3_dir):
        print("🤖 AI 모델 로딩 중... (Whisper Base)")
        self.model = WhisperModel("base", device="cpu", compute_type="int8")
        self.recognizer = sr.Recognizer()
        
        # 🔥 잡음 필터링 강화
        self.recognizer.energy_threshold = 2000  # 더 높게 (배경 소음 무시)
        self.recognizer.dynamic_energy_threshold = False  # 고정값 사용
        
        self.mp3_dir = mp3_dir
        self.mic_index = self.find_pulse_mic()
        print(f"🎤 사용 마이크 번호: {self.mic_index}")
        print(f"📁 MP3 저장 경로: {self.mp3_dir}")

    def find_pulse_mic(self):
        mic_list = sr.Microphone.list_microphone_names()
        for i, name in enumerate(mic_list):
            if 'bluez' in name.lower():  # Bluetooth 우선
                return i
            if 'pulse' in name.lower() or 'default' in name.lower():
                return i
        return None

    def listen(self):
        try:
            mic = sr.Microphone(device_index=self.mic_index, sample_rate=16000)
            with mic as source:
                # 배경 소음 측정 제거 (시간 절약)
                audio = self.recognizer.listen(
                    source, 
                    timeout=10,  # 10초 대기
                    phrase_time_limit=5  # 최대 5초 발화
                )
                return audio
        except:
            return None

    def transcribe(self, audio):
        if audio is None:
            return None
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(audio.sample_width)
            wav_file.setframerate(audio.sample_rate)
            wav_file.writeframes(audio.frame_data)
        wav_buffer.seek(0)
        
        segments, _ = self.model.transcribe(
            wav_buffer,
            language="ko",
            initial_prompt="시각장애인 안내: 앞으로 가, 멈춰, 앞에 뭐가 있어",
            vad_filter=True,  # 음성 구간만 인식
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        return " ".join([seg.text for seg in segments]).strip()

    def speak(self, text, filename="response.mp3"):
        filepath = os.path.join(self.mp3_dir, filename)
        print(f"🗣️ 로봇: {text}")
        try:
            gTTS(text=text, lang='ko').save(filepath)
            os.system(f"play -q {filepath} vol 2.0")
        except:
            pass

class VoiceNode(Node):
    def __init__(self):
        super().__init__('voice_node')
        
        pkg_path = "/root/gae_ws/src/gae_interface"
        self.mp3_dir = os.path.join(pkg_path, "mp3")
        os.makedirs(self.mp3_dir, exist_ok=True)
        
        # 발행 토픽
        self.command_pub = self.create_publisher(String, '/gae_interface/voice/command', 10)
        self.response_pub = self.create_publisher(String, '/gae_interface/voice/response', 10)
        self.status_pub = self.create_publisher(String, '/gae_interface/voice/status', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # 구독 토픽 (YOLO 결과)
        self.yolo_sub = self.create_subscription(
            String,
            '/yolo_result',  # YOLO 토픽명 확인 필요
            self.yolo_callback,
            10
        )
        
        self.latest_object = "아무것도 없습니다"
        self.traffic_light = None  # "red" or "green"
        
        self.bot = VoiceAssistant(self.mp3_dir)
        
        self.voice_thread = threading.Thread(target=self.voice_loop)
        self.voice_thread.daemon = True
        self.voice_thread.start()
        
        self.publish_status("준비 완료")
        print("✅ 시각장애인 안내 로봇 준비 완료!")

    def yolo_callback(self, msg):
        """YOLO 결과 수신"""
        data = msg.data.lower()
        self.latest_object = data
        
        # 신호등 자동 감지
        if "red" in data or "빨간불" in data:
            if self.traffic_light != "red":
                self.traffic_light = "red"
                self.handle_red_light()
        elif "green" in data or "초록불" in data:
            if self.traffic_light != "green":
                self.traffic_light = "green"
                self.handle_green_light()

    def handle_red_light(self):
        """빨간불 → 자동 정지"""
        self.publish_response("빨간불입니다. 멈춥니다")
        self.bot.speak("빨간불입니다. 멈춥니다")
        self.stop_robot()

    def handle_green_light(self):
        """초록불 → 자동 출발"""
        self.publish_response("초록불입니다. 출발합니다")
        self.bot.speak("초록불입니다. 출발합니다")
        # 전진 명령 실행 (예시)
        # os.system("ros2 launch gae_bringup forward.launch.py &")

    def stop_robot(self):
        """로봇 정지"""
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.0
        self.cmd_vel_pub.publish(twist)
        self.get_logger().info("[동작] 정지")

    def publish_status(self, status):
        msg = String()
        msg.data = status
        self.status_pub.publish(msg)

    def publish_command(self, command):
        msg = String()
        msg.data = command
        self.command_pub.publish(msg)

    def publish_response(self, response):
        msg = String()
        msg.data = response
        self.response_pub.publish(msg)

    def process_command(self, text):
        """음성 명령 처리"""
        print(f"📝 인식됨: '{text}'")
        
        # 짧은 잡음 무시
        if len(text) < 2:
            return
        
        # 1. 전진 명령
        if any(x in text for x in ['앞으로', '전진', '가', '출발', '고']):
            self.publish_command(f"전진: {text}")
            self.publish_response("전진합니다")
            self.bot.speak("전진합니다")
            # os.system("ros2 launch gae_bringup forward.launch.py &")
            
        # 2. 정지 명령
        elif any(x in text for x in ['멈춰', '서', '스톱', '정지']):
            self.publish_command(f"정지: {text}")
            self.publish_response("정지합니다")
            self.bot.speak("정지합니다")
            self.stop_robot()
            
        # 3. 전방 확인
        elif any(x in text for x in ['뭐가', '보여', '앞에', '있어']):
            self.publish_command(f"전방 확인: {text}")
            response = f"앞에 {self.latest_object}가 있습니다"
            self.publish_response(response)
            self.bot.speak(response)
        
        else:
            print(f"❌ 명령 불일치: '{text}'")

    def voice_loop(self):
        while rclpy.ok():
            self.publish_status("듣는 중...")
            print("\n👂 듣는 중... (말씀해주세요)")
            
            audio = self.bot.listen()
            
            if audio:
                self.publish_status("분석 중...")
                text = self.bot.transcribe(audio)
                
                if text and len(text) >= 2:
                    self.process_command(text)

def main(args=None):
    os.system("apt-get install -y libsox-fmt-mp3 > /dev/null 2>&1")
    rclpy.init(args=args)
    node = VoiceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
