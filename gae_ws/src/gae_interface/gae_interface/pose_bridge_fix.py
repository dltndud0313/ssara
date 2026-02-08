import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from nav_msgs.msg import Odometry
import json
import time
import math
import paho.mqtt.client as mqtt

class PoseBridgeFix(Node):
    def __init__(self):
        super().__init__('pose_bridge_fix')
        
        # [핵심] SLAM 데이터 유실 방지를 위한 QoS 설정 (Best Effort)
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)

        self.subscription = self.create_subscription(
            Odometry, 
            '/rtabmap/odom', 
            self.listener_callback, 
            qos
        )

        self.broker_address = "localhost"
        self.port = 1883
        self.topic = "robot/pose"

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Taeyeon_Pose_Bridge")
        
        try:
            self.client.connect(self.broker_address, self.port, 60)
            self.client.loop_start()
            print(f"[MQTT] Pose Bridge Connected: {self.broker_address}:{self.port}")
        except Exception as e:
            print(f"[MQTT] Connection Failed: {e}")

        self.last_sent_time = 0.0
        self.last_x = 0.0
        self.last_y = 0.0
        self.initialized = False

    def listener_callback(self, msg):
        current_time = time.time()
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        # [필터 1] (0,0) 원점 리셋 무시 (SLAM 트래킹 로스트 방지)
        if abs(x) < 0.001 and abs(y) < 0.001:
            if self.initialized:
                # print("[Skip] SLAM tracking lost (0,0 reset)")
                pass
            return

        if not self.initialized:
            self.last_x = x
            self.last_y = y
            self.initialized = True
            print(f"[Init] First valid pose: x={x:.3f}, y={y:.3f}")

        # [필터 2] 0.3초 간격 제한 (웹 부하 감소)
        if current_time - self.last_sent_time < 0.3:
            return

        dist = math.sqrt((x - self.last_x)**2 + (y - self.last_y)**2)

        # [필터 3] 1m 이상 순간이동 = SLAM 오류로 간주하고 무시
        if dist > 1.0:
            print(f"[Skip] Jump detected: {dist:.2f}m")
            return

        # [필터 4] 3cm 미만 떨림은 무시 (제자리 정지 시)
        if dist < 0.03:
            return

        payload = {
            'x': round(x, 3), 
            'y': round(y, 3), 
            'state': 'active'
        }
        
        try:
            json_str = json.dumps(payload)
            self.client.publish(self.topic, json_str)
            self.last_sent_time = current_time
            self.last_x = x
            self.last_y = y
            print(f"[Send] {json_str}")
        except Exception as e:
            print(f"[Error] {e}")

    def destroy_node(self):
        self.client.loop_stop()
        self.client.disconnect()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = PoseBridgeFix()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
