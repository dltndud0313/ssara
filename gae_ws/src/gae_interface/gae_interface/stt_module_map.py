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
        print("🤖 AI 모델 로딩 중... (발음 교정 모드)")
        self.model = WhisperModel("base", device="cpu", compute_type="int8")
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 500
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 0.6 
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
        time.sleep(0.05)
        # 소리 작게 (vol 0.1)
        cmd = "play -n -q synth 0.1 sin 800 vol 0.1" if type == "start" else "play -n -q synth 0.1 sin 600 vol 0.1"
        os.system(f"{cmd} > /dev/null 2>&1")
        time.sleep(0.05)

    def listen(self):
        try:
            mic = sr.Microphone(device_index=self.mic_index, sample_rate=16000)
            with mic as source:
                self.play_beep("start")
                print("👂 말씀하세요...")
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

        # [수정] 오인식 되는 단어들을 프롬프트에 힌트로 넣어줌
        context_words = (
            "싸라, 사라, 자라,"
            "앞으로 가, 액수로 가, 압도도 가, 앗으로 가, 아프로 가,"
            "멈춰, 멈췄어, 서, 스톱, 정지,"
            "병원, 약국, 싸피, 싹키, 사피, 좌키,"
            "데리러, 젤리로, 데리고,"
            "지금 몇 시야"
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
        self.yolo_sub = self.create_subscription(Int32, '/yolo_detection/class_id', self.yolo_callback, 10)
        
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        try:
            self.mqtt_client.connect(os.getenv('MQTT_BROKER', 'localhost'), int(os.getenv('MQTT_PORT', '1883')), 60)
            self.mqtt_client.loop_start()
        except: pass

        self.bot = VoiceAssistant(self.mp3_dir)
        self.last_warning_time = 0
        
        threading.Thread(target=self.voice_loop, daemon=True).start()
        print("✅ 로봇 '싸라' 준비 완료 (발음 교정 Ver)")

    def yolo_callback(self, msg):
        class_id = msg.data
        if time.time() - self.last_warning_time < 3.0: return
        if class_id == 0: # 빨간불
            self.execute_node("stop", "빨간불입니다! 정지합니다.")
            self.last_warning_time = time.time()

    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode('utf-8')
            try: data = json.loads(payload)
            except: data = {"type": "text", "text": payload}
            
            if msg.topic == "/gae/map_to_voice":
                target = data.get("target", "목적지")
                distance = data.get("distance", "")
                if distance: response = f"{target}까지 {distance} 남았습니다."
                else: response = f"{target} 위치를 찾았습니다. 안내를 시작합니다."
                self.bot.speak(response)
                self.log_and_send(f"[로봇] {response}", "robot")

            elif msg.topic == "/gae/web_to_voice":
                self.bot.speak(f"보호자 메시지. {data.get('text', payload)}")
        except: pass

    def on_mqtt_connect(self, client, userdata, flags, rc):
        client.subscribe("/gae/web_to_voice")
        client.subscribe("/gae/map_to_voice")

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
        self.bot.speak(response_text)
        self.log_and_send(f"[로봇] {response_text}", "robot")
        node_map = {"forward": "ros2 launch gae_control forward.launch.py", "stop": "ros2 launch gae_control stop.launch.py"}
        if action in node_map:
            try: 
                proc = subprocess.Popen(node_map[action].split())
                self.log_and_send(f"[실행] {action} 노드 (PID: {proc.pid})", "action")
            except Exception as e: 
                self.log_and_send(f"[에러] {action} 실패: {e}", "error")

    def publish_status(self, status):
        msg = String(); msg.data = status; self.status_pub.publish(msg)

    # =========================================================
    # [핵심 수정] 오인식 단어 처리 (여기가 바뀜)
    # =========================================================
    def process_command(self, text):
        self.log_and_send(f"[사용자] {text}", "user")

        # 1. 🚨 긴급 정지 (멈췄어, 서, 정지)
        # '멈췄어'를 시간에서 빼고 여기로 가져옴!
        if any(x in text for x in ['서', '서!', '멈춰', '스톱', '정지', '위험해', '멈췄어']):
            self.execute_node("stop", "멈추겠습니다.")
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

        # 4. ⏰ 시간 (멈췄어 삭제됨)
        # 이제 '멈춰'랑 헷갈려서 시간 말하는 일 없음
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

        # 6. 🚗 주행 명령 (오인식 단어 추가!)
        # 액수로, 압도도, 앗으로, 아프로 -> 전부 '앞으로' 취급
        if any(x in text for x in ['앞으로', '전진', '출발', '액수로', '압도도', '앗으로', '아프로']):
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

