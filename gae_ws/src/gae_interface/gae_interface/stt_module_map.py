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

class VoiceAssistant:
    def __init__(self, mp3_dir):
        # Base 모델 (속도 중심)
        print("🤖 AI 모델 로딩 중... (Volume Down + Smart Logic)")
        self.model = WhisperModel("base", device="cpu", compute_type="int8")

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 500
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 0.8
        
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
        # [수정 1] 소리 대폭 감소 (vol 0.5 -> 0.1)
        # 귀 아프지 않게 아주 작게 '띠링'
        cmd = "play -n -q synth 0.1 sin 800 vol 0.1" if type == "start" else "play -n -q synth 0.1 sin 600 vol 0.1"
        os.system(f"{cmd} > /dev/null 2>&1")

    def listen(self):
        try:
            mic = sr.Microphone(device_index=self.mic_index, sample_rate=16000)
            with mic as source:
                self.play_beep("start") # 띠링
                print("👂 말씀하세요...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                self.play_beep("end")   # 띠롱
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

        # [수정 2] '가줘' 추가 및 장소 키워드 강화
        context_words = (
            "싸라, 사라, 자라, 살아냐, 싸다,"
            "싸피, 싹키, 사피, 좌키, 병원, 약국,"
            "데리러, 젤리로, 데리고, 고자에게,"
            "지금 몇 시야, 멈췄어, 멈췄니,"
            "앞으로 가, 멈춰, 가줘, 해줘"
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
        filepath = os.path.join(self.mp3_dir, filename)
        print(f"🗣️ 로봇: {text}")
        try:
            # [수정 3] 목소리 볼륨 감소 (vol 3.0 -> 1.0 기본값)
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
        self.response_pub = self.create_publisher(String, '/gae_interface/voice/response', 10)
        self.status_pub = self.create_publisher(String, '/gae_interface/voice/status', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.yolo_sub = self.create_subscription(Int32, '/yolo_detection/class_id', self.yolo_callback, 10)
        self.latest_object = "아무것도 없습니다"
        
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        try:
            self.mqtt_client.connect(os.getenv('MQTT_BROKER', 'localhost'), int(os.getenv('MQTT_PORT', '1883')), 60)
            self.mqtt_client.loop_start()
        except: pass

        self.bot = VoiceAssistant(self.mp3_dir)
        threading.Thread(target=self.voice_loop, daemon=True).start()
        self.publish_status("준비 완료")
        print("✅ 로봇 '싸라' 준비 완료 (Volume Fix + Navigation Fix)")

    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode('utf-8')
            try: data = json.loads(payload)
            except: data = {"type": "text", "text": payload}
            
            if msg.topic == "/gae/map_to_voice" and data.get("type") == "map":
                target = data.get("target", "목적지")
                self.bot.speak(f"알겠습니다. {target}으로 안내할게요.")
            elif msg.topic == "/gae/web_to_voice":
                self.bot.speak(f"보호자 메시지. {data.get('text', payload)}")
        except: pass

    def on_mqtt_connect(self, client, userdata, flags, rc):
        client.subscribe("/gae/web_to_voice")
        client.subscribe("/gae/map_to_voice")

    def mqtt_publish(self, topic, message, msg_type="conversation"):
        try:
            payload = json.dumps({ "type": msg_type, "message": message, "timestamp": datetime.now().isoformat() }, ensure_ascii=False)
            self.mqtt_client.publish(topic, payload)
        except: pass

    def log_and_send(self, message, msg_type="conversation"):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.mqtt_publish("/gae/voice_to_web", message, msg_type)

    def yolo_callback(self, msg):
        class_id = msg.data
        if class_id == 0: self.latest_object = "빨간불"
        elif class_id == 1: self.latest_object = "초록불"
        elif class_id == 2: self.latest_object = "횡단보도 정지선"
        else: self.latest_object = "장애물"

    def execute_node(self, action, response_text):
        self.bot.speak(response_text)
        self.log_and_send(f"[로봇] {response_text}", "robot")
        node_map = { "forward": "ros2 launch gae_control forward.launch.py", "stop": "ros2 launch gae_control stop.launch.py" }
        if action in node_map:
            try: subprocess.Popen(node_map[action].split())
            except: pass
    
    def publish_status(self, status):
        msg = String(); msg.data = status; self.status_pub.publish(msg)

    # [수정된 로직]
    def process_command(self, text):
        self.log_and_send(f"[사용자] {text}", "user")

        # 1. 🐶 호출어
        if any(text.startswith(x) for x in ['싸', '사', '자', '살', '따', '아']): 
            response = "네! 말씀하세요."
            self.bot.speak(response)
            self.log_and_send(f"[로봇] {response}", "robot")
            return

        # 2. 🆘 보호자
        if any(x in text for x in ['데리', '보호자', '도와', '젤리', '탈리', '보고자', '와달', '오라고', '고자']):
            self.mqtt_publish("/gae/voice_to_web", "사용자 호출! 데리러 와주세요.", "emergency")
            response = "보호자에게 연락했습니다."
            self.bot.speak(response)
            self.log_and_send(f"[로봇] {response}", "robot")
            return

        # 3. ⏰ 시간
        if any(x in text for x in ['시간', '몇', '언제', '멈췄어', '멈췄니']):
            now = datetime.now()
            ampm = "오전" if now.hour < 12 else "오후"
            h = now.hour if now.hour <= 12 else now.hour - 12
            response = f"현재 {ampm} {h}시 {now.minute}분입니다."
            self.bot.speak(response)
            self.log_and_send(f"[로봇] {response}", "robot")
            return

        # 4. 🗺️ 장소 (여기가 핵심!)
        # "병원으로 가줘" -> '병원'만 들려도 바로 반응하게 변경
        # "가자", "가줘", "안내" 등 뒤에 뭐가 붙든 상관없이 장소 키워드 우선 체크
        if any(x in text for x in ['병원', '약국', '집', '싸피', '싹키', '사피', '좌키', '쌓피', '은행', '어디', '가자', '안내', '가줘']):
            target = ""
            if '병원' in text: target = "병원"
            elif '약국' in text: target = "약국"
            elif '집' in text: target = "집"
            elif '은행' in text: target = "은행"
            elif any(s in text for s in ['싸피', '싹키', '사피', '좌키', '쌓피']): target = "싸피"
            
            if target:
                response = f"{target}으로 안내할게요."
                self.mqtt_publish("/gae/voice_to_map", target, "search")
                self.bot.speak(response)
                self.log_and_send(f"[로봇] {response}", "robot")
                return # 여기서 바로 종료 (중요)
            elif any(x in text for x in ['어디', '가자', '안내', '가줘']): # 장소는 없는데 가자고만 한 경우
                self.bot.speak("어디로 갈까요?")
                return

        # 5. 🚦 상황
        if any(x in text for x in ['뭐가', '뭐 있', '보여', '상황']):
            obj = self.latest_object
            if "아무것도" in obj: resp = "아무것도 없습니다."
            else: resp = f"앞에 {obj}가 있습니다."
            self.bot.speak(resp)
            self.log_and_send(f"[로봇] {resp}", "robot")
            return

        # 6. 🚗 주행
        if any(x in text for x in ['멈춰', '서', '스톱', '정지']):
            self.execute_node("stop", "멈추겠습니다.")
            return
        if any(x in text for x in ['앞으로', '전진', '출발']):
            self.execute_node("forward", "앞으로 갑니다.")
            return

        # 못 알아들음
        self.bot.speak("다시 말씀해 주세요.")

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
