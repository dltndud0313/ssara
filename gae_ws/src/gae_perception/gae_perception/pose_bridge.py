import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import json
import time
import math
import paho.mqtt.client as mqtt

class PoseBridge(Node):
    def __init__(self):
        super().__init__('pose_bridge')
        
        self.subscription = self.create_subscription(
            PoseStamped,
            '/slam_pose', 
            self.listener_callback,
            10
        )
        
        # [수정 완료] 제슨 나노 내부의 Mosquitto 브로커를 사용합니다.
        self.broker_address = "192.168.100.246" 
        self.port = 1884
        self.topic = "robot/pose"         
        
        # 클라이언트 이름도 깔끔하게 정리
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Jetson_Robot_Bridge")
        
        try:
            self.client.connect(self.broker_address, self.port, 60)
            self.client.loop_start() 
            print(f"[MQTT] Local Broker Connected: {self.broker_address}:{self.port}")
        except Exception as e:
            print(f"[MQTT] Connection Failed: {e}")

        self.last_sent_time = 0.0
        self.last_x = 0.0
        self.last_y = 0.0

    def listener_callback(self, msg):
        current_time = time.time()
        x = msg.pose.position.x
        y = msg.pose.position.y
        
        # 0.1초 제한
        if current_time - self.last_sent_time < 0.1:
            return
            
        # 1cm 이동 제한
        dist = math.sqrt((x - self.last_x)**2 + (y - self.last_y)**2)
        if dist < 0.01:
            return 

        payload = {
            'x': round(x, 2),
            'y': round(y, 2),
            'state': 'active'
        }
        
        try:
            json_str = json.dumps(payload)
            self.client.publish(self.topic, json_str)
            
            self.last_sent_time = current_time
            self.last_x = x
            self.last_y = y
            print(f"[Send] {json_str}") # 데이터 나가는지 터미널에 출력
            
        except Exception as e:
            print(f"[Error] Failed to publish message: {e}")

    def destroy_node(self):
        self.client.loop_stop()
        self.client.disconnect()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = PoseBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()