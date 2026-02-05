import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32
from geometry_msgs.msg import Twist
import threading
import speech_recognition as sr
from faster_whisper import WhisperModel
from gtts import gTTS
import os
import io
import wave
import subprocess
import paho.mqtt.client as mqtt
import json
from datetime import datetime

# =========================================================
# 1. VoiceAssistant (음성 처리 전담 클래스)
# =========================================================
class VoiceAssistant:
    def __init__(self, mp3_dir):
        print("🤖 AI 모델 로딩 중... (Whisper Base + MQTT)")
        # [복구] 잘린 부분 수정 (int8)
        self.model = WhisperModel("base", device="cpu", compute_type="int8")
        
        self.recognizer = sr.Recognizer()
        # [중요] 시끄러운 환경 대응 설정
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 0.8
        
        self.mp3_dir = mp3_dir
        self.mic_index = self.find_pulse_mic()
        print(f"🎤 사용 마이크 번호: {self.mic_index}")

    def find_pulse_mic(self):
        # PulseAudio 또는 Bluez(버즈) 마이크 찾기
        mic_list = sr.Microphone.list_microphone_names()
        for i, name in enumerate(mic_list):
            if 'bluez' in name.lower():
                return i
            if 'pulse' in name.lower() or 'default' in name.lower():
                return i
        return None

    def listen(self):
        try:
            mic = sr.Microphone(device_index=self.mic_index, sample_rate=16000)
            with mic as source:
                # [복구] 잘린 파라미터 수정
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                return audio
        except Exception as e:
            # print(f"Listen Error: {e}") # 디버깅 시 주석 해제
            return None

    def transcribe(self, audio):
        if audio is None:
            return None
        
        # 오디오 데이터 변환
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(audio.sample_width)
            wav_file.setframerate(audio.sample_rate)
            wav_file.writeframes(audio.frame_data)
        wav_buffer.seek(0)

        # Whisper 추론
        # [복구] 잘린 프롬프트 수정
        segments, _ = self.model.transcribe(
            wav_buffer,
            language="ko",
            initial_prompt="시각장애인 안내: 앞으로 가, 멈춰, 앞에 뭐가 있어?, 싸피, 횡단보도, 신호등",
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        return " ".join([seg.text for seg in segments]).strip()

    def speak(self, text, filename="response.mp3"):
        filepath = os.path.join(self.mp3_dir, filename)
        print(f"🗣️ 로봇: {text}")
        try:
            # gTTS 저장 및 재생
            gTTS(text=text, lang='ko').save(filepath)
            # [팁] vol 3.0으로 소리 더 키움
            os.system(f"play -q {filepath} vol 3.0")
        except Exception as e:
            print(f"TTS Error: {e}")

# =========================================================
# 2. VoiceNode (ROS2 + MQTT 통신 담당)
# =========================================================
class VoiceNode(Node):
    def __init__(self):
        super().__init__('voice_node')

        pkg_path = "/root/gae_ws/src/gae_interface"
        self.mp3_dir = os.path.join(pkg_path, "mp3")
        os.makedirs(self.mp3_dir, exist_ok=True)

        # 대화 로그 설정
        self.log_dir = os.path.join(pkg_path, "conversation_logs")
        os.makedirs(self.log_dir, exist_ok=True)
        # [복구] 파일명 포맷 수정
        self.log_file = os.path.join(self.log_dir, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

        # ROS2 Pub/Sub
        self.command_pub = self.create_publisher(String, '/gae_interface/voice/command', 10)
        self.response_pub = self.create_publisher(String, '/gae_interface/voice/response', 10)
        self.status_pub = self.create_publisher(String, '/gae_interface/voice/status', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # YOLO 구독
        self.yolo_sub = self.create_subscription(
            Int32,
            '/yolo_detection/class_id',
            self.yolo_callback,
            10
        )

        self.latest_object = "아무것도 없습니다"
        self.latest_class_id = None

        # MQTT 클라이언트 설정
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message

        mqtt_broker = os.getenv('MQTT_BROKER', 'localhost') # 또는 호스트 IP (172.17.0.1)
        mqtt_port = int(os.getenv('MQTT_PORT', '1883'))

        try:
            self.mqtt_client.connect(mqtt_broker, mqtt_port, 60)
            self.mqtt_client.loop_start()
            self.get_logger().info(f"📡 MQTT 연결 성공: {mqtt_broker}:{mqtt_port}")
        except Exception as e:
            self.get_logger().error(f"❌ MQTT 연결 실패: {e}")

        # 봇 초기화
        self.bot = VoiceAssistant(self.mp3_dir)

        # 음성 인식 쓰레드 시작
        self.voice_thread = threading.Thread(target=self.voice_loop)
        self.voice_thread.daemon = True
        self.voice_thread.start()

        self.publish_status("준비 완료")
        print("✅ 시각장애인 안내 로봇 준비 완료 (Map Mode)")

    # -------------------------------------------------------------
    # [수정됨] MQTT 메시지 처리 함수 (JSON 파싱 로직 추가)
    # -------------------------------------------------------------
    def on_mqtt_message(self, client, userdata, msg):
        """웹에서 온 메시지 처리 (지도/텍스트 구분)"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            self.get_logger().info(f"📩 Raw MQTT 수신: {payload}")

            # 1. JSON 파싱 시도
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                # JSON이 아니면 옛날 방식(단순 텍스트)으로 처리
                data = {"type": "text", "text": payload}

            # 2. 토픽별 처리
            if topic == "/gae/map_to_voice":
                # 지도 목적지 정보 처리
                # 예: {"type": "map", "target": "싸피 1캠퍼스", "lat": 35.xxx, "lon": 126.xxx}
                if isinstance(data, dict) and data.get("type") == "map":
                    target = data.get("target", "목적지")
                    
                    # 로봇 응답
                    response_text = f"알겠습니다. {target}로 안내를 시작할게요."
                    self.get_logger().info(f"📍 지도 명령 수신: {target}")
                    
                    # 로그 저장 및 전송
                    self.log_and_send(f"[지도요청] {target}", "map")
                    
                    # 음성 안내
                    self.bot.speak(response_text)
                    self.log_and_send(f"[로봇] {response_text}", "robot")
                    
                    # (추후 여기에 네비게이션 Action Client 코드 추가)
                else:
                    self.get_logger().warn("지도 토픽인데 형식이 안 맞습니다.")

            elif topic == "/gae/web_to_voice":
                # 보호자 메시지 처리
                # 예: {"text": "밥 먹어"} 또는 그냥 "밥 먹어"
                text_msg = data.get("text", payload) if isinstance(data, dict) else payload
                
                message = f"보호자 메시지입니다. {text_msg}"
                self.log_and_send(f"[보호자] {text_msg}", "guardian")
                
                self.bot.speak(message)
                self.log_and_send(f"[로봇] {message}", "robot")

        except Exception as e:
            self.get_logger().error(f"❌ MQTT 메시지 처리 오류: {e}")

    def on_mqtt_connect(self, client, userdata, flags, rc):
        self.get_logger().info(f"📡 MQTT 연결 코드: {rc}")
        client.subscribe("/gae/web_to_voice")  # 보호자 메시지
        client.subscribe("/gae/map_to_voice")  # 지도 목적지 [중요]

    def mqtt_publish(self, topic, message, msg_type="conversation"):
        try:
            payload = json.dumps({
                "type": msg_type,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False)

            self.mqtt_client.publish(topic, payload)
        except Exception as e:
            self.get_logger().error(f"❌ MQTT 발행 실패: {e}")

    def log_and_send(self, message, msg_type="conversation"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}"

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + "\n")

        self.mqtt_publish("/gae/voice_to_web", message, msg_type)

    def yolo_callback(self, msg):
        class_id = msg.data
        self.latest_class_id = class_id

        if class_id == 0:
            self.latest_object = "빨간불"
            # self.handle_red_light() # 너무 자주 말하면 시끄러우니 필요시 주석 해제
        elif class_id == 1:
            self.latest_object = "초록불"
            # self.handle_green_light()
        elif class_id == 2:
            self.latest_object = "횡단보도 정지선"
            self.handle_stop_marker()
        else:
            self.latest_object = "장애물"

    def handle_stop_marker(self):
        # 중복 안내 방지 로직이 필요할 수 있음
        msg = "횡단보도 정지선입니다. 신호를 확인하세요"
        self.bot.speak(msg)
        self.log_and_send(f"[YOLO] {msg}", "yolo")
        self.execute_node("stop")

    def execute_node(self, action):
        node_map = {
            "forward": "ros2 launch gae_control forward.launch.py",
            "stop": "ros2 launch gae_control stop.launch.py",
        }
        if action in node_map:
            try:
                subprocess.Popen(node_map[action].split())
                self.log_and_send(f"[실행] {action} 노드", "action")
            except Exception as e:
                self.get_logger().error(f"❌ 노드 실행 실패: {e}")

    def publish_status(self, status):
        msg = String()
        msg.data = status
        self.status_pub.publish(msg)

    def process_command(self, text):
        self.log_and_send(f"[사용자] {text}", "user")

        # 1. 위치 검색 요청 (웹으로 전송)
        if any(x in text for x in ['근처', '어디', '병원', '약국', '학교', '싸피']):
            self.log_and_send(f"[검색 요청] {text}", "search_request")
            # 웹에게 "검색해줘"라고 요청 보냄 (type: search)
            self.mqtt_publish("/gae/voice_to_map", text, "search") 
            
            response = "위치를 검색하고 있습니다."
            self.bot.speak(response)
            self.log_and_send(f"[로봇] {response}", "robot")

        # 2. 전방 확인
        elif any(x in text for x in ['뭐가 있어', '뭐 있어', '뭐 보여']):
            response = f"앞에 {self.latest_object}가 있습니다"
            self.bot.speak(response)
            self.log_and_send(f"[로봇] {response}", "robot")

        # 3. 정지
        elif any(x in text for x in ['멈춰', '서', '스톱', '정지']):
            response = "정지합니다"
            self.bot.speak(response)
            self.execute_node("stop")

        # 4. 전진
        elif any(x in text for x in ['앞으로', '전진', '출발']):
            response = "앞으로 가겠습니다"
            self.bot.speak(response)
            self.execute_node("forward")
        
        else:
            # 인식은 했으나 명령어가 아님
            pass

    def voice_loop(self):
        while rclpy.ok():
            self.publish_status("듣는 중...")
            audio = self.bot.listen()

            if audio:
                self.publish_status("분석 중...")
                text = self.bot.transcribe(audio)

                if text and len(text) >= 1: # 1글자라도 인식하면 처리
                    print(f"📝 인식됨: {text}")
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
