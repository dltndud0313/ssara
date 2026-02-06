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
import time
from datetime import datetime, timedelta, timezone

class VoiceAssistant:
    def __init__(self, mp3_dir):
        print("🤖 AI 모델 로딩 중... (Active Safety + Nav Mode)")
        self.model = WhisperModel("base", device="cpu", compute_type="int8")
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 500
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 0.6 # 짧은 단어(서!) 캐치 위해 줄임
        self.mp3_dir = mp3_dir
        self.mic_index = self.find_pulse_mic()
        print(f"🎤 사용 마이크 번호: {self.mic_index}")

    def find_pulse_mic(self):
        mic_list = sr.Microphone.list_microphone_names()
        for i, name in enumerate(mic_list):
            if 'bluez' in name.lower(): return i
            if 'pulse' in name.lower() or 'default' in name.lower(): return i
        return None

    def play_beep(self, type="start"):
        # 지직거림 방지: 소리 재생 전후로 약간의 텀을 줌
        time.sleep(0.05)
        cmd = "play -n -q synth 0.1 sin 800 vol 0.1" if type == "start" else "play -n -q synth 0.1 sin 600 vol 0.1"
        os.system(f"{cmd} > /dev/null 2>&1")
        time.sleep(0.05)

    def listen(self):
        try:
            mic = sr.Microphone(device_index=self.mic_index, sample_rate=16000)
            with mic as source:
                self.play_beep("start")
                print("👂 말씀하세요...")
                # phrase_time_limit을 줄여서 짧게 치고 빠지게 함
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                self.play_beep("end")
                return audio
        except:
            return None

    def transcribe(self, audio):
        if audio is None: return None
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(audio.sample_width)
            wav_file.setframerate(audio.sample_rate)
            wav_file.writeframes(audio.frame_data)
        wav_buffer.seek(0)

        # [강화] "서!", "멈춰!" 같은 단발마 명령어 대거 추가
        context_words = (
            "싸라, 사라, 자라, 살아냐,"
            "서, 서!, 멈춰, 스톱, 정지, 위험해,"
            "병원, 약국, 싸피, 싹키, 사피, 좌키,"
            "데리러, 젤리로, 데리고,"
            "지금 몇 시야, 앞으로 가, 가줘, 해줘"
        )

        segments, _ = self.model.transcribe(
            wav_buffer,
            language="ko",
            initial_prompt=context_words,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        return " ".join([seg.text for seg in segments]).strip()

    def speak(self, text, filename="response.mp3"):
        # 말하는 중엔 듣기 멈추기 위해 Lock 필요하지만 일단 간단히 구현
        filepath = os.path.join(self.mp3_dir, filename)
        print(f"🗣️ 로봇: {text}")
        try:
            gTTS(text=text, lang='ko').save(filepath)
            os.system(f"play -q {filepath} vol 1.0")
        except: pass

class VoiceNode(Node):
    def __init__(self):
        super().__init__('voice_node')
        
        pkg_path = "/root/gae_ws/src/gae_interface"
        self.mp3_dir = os.path.join(pkg_path, "mp3")
        os.makedirs(self.mp3_dir, exist_ok=True)
        self.log_file = os.path.join(pkg_path, "conversation_logs", f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

        self.command_pub = self.create_publisher(String, '/gae_interface/voice/command', 10)
        self.status_pub = self.create_publisher(String, '/gae_interface/voice/status', 10)
        
        # [NEW] YOLO 데이터를 실시간으로 감시
        self.yolo_sub = self.create_subscription(Int32, '/yolo_detection/class_id', self.yolo_callback, 10)
        
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        try:
            self.mqtt_client.connect(os.getenv('MQTT_BROKER', 'localhost'), int(os.getenv('MQTT_PORT', '1883')), 60)
            self.mqtt_client.loop_start()
        except: pass

        self.bot = VoiceAssistant(self.mp3_dir)
        self.is_speaking = False # 말하는 중인지 체크 (중복 방지)
        
        # 중복 경고 방지용 타이머
        self.last_warning_time = 0
        
        threading.Thread(target=self.voice_loop, daemon=True).start()
        print("✅ 로봇 '싸라' 준비 완료 (Red Light Stop + Turn-by-Turn)")

    # [핵심] YOLO 실시간 감시 및 자동 행동
    def yolo_callback(self, msg):
        class_id = msg.data
        current_time = time.time()
        
        # 3초에 한 번만 경고 (너무 시끄럽지 않게)
        if current_time - self.last_warning_time < 3.0:
            return

        if class_id == 0: # 빨간불 (Red Light)
            print("🚨 빨간불 감지! 강제 정지!")
            self.execute_node("stop", "빨간불입니다! 정지합니다.")
            self.last_warning_time = current_time
            
        elif class_id == 2: # 횡단보도 정지선
            # 정지선은 안내만 하고 멈출지 말지는 판단 필요 (일단 안내만)
            self.bot.speak("전방에 정지선이 있습니다.")
            self.last_warning_time = current_time
            
        elif class_id == 3: # 장애물 (Obstacle)
            # 장애물 발견 시 경고 (회피는 네비게이션 노드의 영역)
            self.bot.speak("장애물이 감지되었습니다. 주의하세요.")
            self.last_warning_time = current_time

    # [핵심] MQTT 메시지 수신 (네비게이션 안내 + 보호자)
    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode('utf-8')
            try: data = json.loads(payload)
            except: data = {"type": "text", "text": payload}
            
            # 1. 지도/네비게이션 안내 메시지
            if msg.topic == "/gae/map_to_voice":
                msg_type = data.get("type", "")
                
                if msg_type == "nav_guide": 
                    # 예: "잠시 후 우회전입니다", "목적지에 도착했습니다"
                    guide_text = data.get("text", "")
                    self.bot.speak(guide_text)
                    self.log_and_send(f"[네비] {guide_text}", "robot")
                    
                elif msg_type == "map":
                    # 기존 목적지 도착/거리 안내
                    target = data.get("target", "목적지")
                    distance = data.get("distance", "")
                    if distance: response = f"{target}까지 {distance} 남았습니다."
                    else: response = f"{target} 위치를 찾았습니다. 안내를 시작합니다."
                    self.bot.speak(response)
                    self.log_and_send(f"[로봇] {response}", "robot")

            # 2. 보호자 메시지
            elif msg.topic == "/gae/web_to_voice":
                self.bot.speak(f"보호자 메시지. {data.get('text', payload)}")
                
        except: pass

    def on_mqtt_connect(self, client, userdata, flags, rc):
        client.subscribe("/gae/web_to_voice")
        client.subscribe("/gae/map_to_voice") # 네비게이션 안내도 여기서 받음

    def mqtt_publish(self, topic, message, msg_type="conversation"):
        try:
            payload = json.dumps({"type": msg_type, "message": message, "timestamp": datetime.now().isoformat()}, ensure_ascii=False)
            self.mqtt_client.publish(topic, payload)
        except: pass

    def log_and_send(self, message, msg_type="conversation"):
        kst = timezone(timedelta(hours=9))
        kst_now = datetime.now(kst)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{kst_now.strftime('%H:%M:%S')}] {message}\n")
        self.mqtt_publish("/gae/voice_to_web", message, msg_type)

    def execute_node(self, action, response_text):
        # 말부터 하고
        self.bot.speak(response_text)
        self.log_and_send(f"[로봇] {response_text}", "robot")
        
        # 진짜 실행
        node_map = {"forward": "ros2 launch gae_control forward.launch.py", "stop": "ros2 launch gae_control stop.launch.py"}
        if action in node_map:
            try: 
                proc = subprocess.Popen(node_map[action].split())
                self.log_and_send(f"[실행] {action} 노드 (PID: {proc.pid})", "action")
            except Exception as e: 
                self.log_and_send(f"[에러] {action} 실패: {e}", "error")

    def publish_status(self, status):
        msg = String(); msg.data = status; self.status_pub.publish(msg)

    def process_command(self, text):
        self.log_and_send(f"[사용자] {text}", "user")

        # 1. 🚨 긴급 정지 (서! 서! 등) - 최우선 순위
        if any(x in text for x in ['서', '서!', '멈춰', '스톱', '정지', '위험해']):
            self.execute_node("stop", "비상 정지합니다!")
            return

        # 2. 🐶 호출어
        if any(text.startswith(x) for x in ['싸라', '사라', '자라']): 
            self.bot.speak("네!")
            return

        # 3. 🆘 보호자
        if any(x in text for x in ['데리', '보호자', '도와', '젤리', '탈리', '고자']):
            self.mqtt_publish("/gae/voice_to_web", "사용자 호출! 데리러 와주세요.", "emergency")
            self.bot.speak("보호자에게 연락했습니다.")
            self.log_and_send("[로봇] 보호자에게 연락했습니다.", "robot")
            return

        # 4. ⏰ 시간
        if any(x in text for x in ['시간', '몇 시', '언제']):
            kst = timezone(timedelta(hours=9))
            now = datetime.now(kst)
            response = f"현재 {now.hour}시 {now.minute}분입니다."
            self.bot.speak(response)
            self.log_and_send(f"[로봇] {response}", "robot")
            return

        # 5. 🗺️ 장소 (검색 요청)
        if any(x in text for x in ['병원', '약국', '집', '싸피', '싹키', '사피', '좌키', '은행', '가자', '가줘']):
            target = "싸피" if any(s in text for s in ['싸피', '싹키', '좌키']) else ("병원" if "병원" in text else ("약국" if "약국" in text else "목적지"))
            
            response = f"{target} 위치를 검색하고 있습니다."
            self.bot.speak(response)
            self.log_and_send(f"[로봇] {response}", "robot")
            self.mqtt_publish("/gae/voice_to_map", target, "search")
            return 

        # 6. 주행 명령
        if any(x in text for x in ['앞으로', '전진', '출발']):
            self.execute_node("forward", "앞으로 갑니다.")
            return

    def voice_loop(self):
        while rclpy.ok():
            self.publish_status("듣는 중...")
            audio = self.bot.listen()
            if audio:
                self.publish_status("분석 중...")
                text = self.bot.transcribe(audio)
                if text and len(text) >= 1: 
                    print(f"📝 인식됨: {text}")
                    self.process_command(text)

def main(args=None):
    rclpy.init(args=args)
    node = VoiceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
