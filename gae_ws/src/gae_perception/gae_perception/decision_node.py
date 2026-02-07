import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import json
import numpy as np

class DecisionNode(Node):
    def __init__(self):
        super().__init__('decision_node')

        # [구독] YOLO 객체 인식 결과 수신
        self.yolo_sub = self.create_subscription(
            String, 
            '/gae_perception/yolo_result', 
            self.yolo_callback, 
            10
        )
        
        # [구독] Depth 카메라 이미지 수신 (물리적 거리 측정용)
        self.depth_sub = self.create_subscription(
            Image, 
            '/camera/depth/image_raw', 
            self.depth_callback, 
            10
        )
        
        # [발행] 로봇 이동 명령 (Twist) 전송 토픽: /cmd_vel
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.bridge = CvBridge()
        
        # [상태 변수] 3방향 거리 데이터 (초기값: 99.9m)
        self.dist_left = 99.9
        self.dist_center = 99.9
        self.dist_right = 99.9
        
        self.detected_objects = []       # YOLO 인식 객체 리스트
        
        # [타이머] 0.1초마다 판단 로직 실행
        self.create_timer(0.1, self.control_loop)
        
        print("[System] Decision Node Started. Logic: Obstacle Avoidance + Traffic Rules")

    def depth_callback(self, msg):
        """
        깊이 카메라 이미지를 받아 화면을 좌/중/우 3분할하고,
        각 영역의 장애물 거리를 계산하여 업데이트합니다.
        """
        try:
            # ROS 이미지를 OpenCV 포맷으로 변환
            depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            h, w = depth_image.shape
            
            # 관심 영역(ROI) 설정: 바닥과 천장을 제외한 화면 중간 1/3 영역만 사용
            roi_y_start = h // 3
            roi_y_end = 2 * h // 3
            roi_img = depth_image[roi_y_start:roi_y_end, :]
            
            # 가로 영역을 3등분 (좌측, 중앙, 우측)
            w_third = w // 3
            
            # 1. Left Zone (왼쪽)
            left_crop = roi_img[:, 0:w_third]
            self.dist_left = self.get_median_dist(left_crop)
            
            # 2. Center Zone (중앙 - 주행 경로)
            center_crop = roi_img[:, w_third:2*w_third]
            self.dist_center = self.get_median_dist(center_crop)
            
            # 3. Right Zone (오른쪽)
            right_crop = roi_img[:, 2*w_third:w]
            self.dist_right = self.get_median_dist(right_crop)
            
        except Exception:
            pass

    def get_median_dist(self, crop_img):
        """
        이미지 영역에서 0(에러값)을 제외한 유효 거리의 중간값을 계산합니다.
        평균값보다 노이즈(튀는 값)에 강합니다.
        """
        valid = crop_img[crop_img > 0]
        if len(valid) > 0:
            return np.median(valid) / 1000.0 # mm 단위를 m 단위로 변환
        else:
            return 99.9 # 유효한 값이 없으면 장애물 없음으로 간주

    def yolo_callback(self, msg):
        """
        YOLO 노드에서 보낸 JSON 데이터를 파싱하여 리스트에 저장합니다.
        """
        try:
            self.detected_objects = json.loads(msg.data)
        except ValueError:
            self.detected_objects = []

    def control_loop(self):
        """
        센서 데이터를 종합하여 로봇의 행동을 결정하고 명령을 내립니다.
        """
        twist = Twist()
        
        # --- [1단계] 상황 인지 (Perception) ---
        is_at_stop_point = False
        traffic_light = "NONE" # 상태: RED, GREEN, NONE
        
        for obj in self.detected_objects:
            name = obj['class'].lower()
            dist = obj['dist_m']
            score = obj['score']
            
            # 스탑포인트 인식: 이름에 stop 포함, 거리 1.2m 이내, 신뢰도 50% 이상
            if "stop" in name and dist < 1.2 and score > 0.5:
                is_at_stop_point = True
            
            # 신호등 인식: 거리 2.5m 이내
            if dist < 2.5:
                if "red" in name:
                    traffic_light = "RED"
                elif "green" in name:
                    traffic_light = "GREEN"

        # --- [2단계] 행동 결정 (Decision making with Priority) ---
        
        # [우선순위 0] 장애물 회피 (Obstacle Avoidance)
        # 전방 1.0m 이내에 장애물(사람, 벽, 나무 등) 감지 시 회피 기동
        if self.dist_center < 1.0:
            print(f"[AVOID] Obstacle detected at {self.dist_center:.2f}m. Calculating path...")
            
            # 안전을 위해 전진 속도 정지
            twist.linear.x = 0.0
            
            # 좌측과 우측 거리 비교하여 더 넓은 쪽으로 회전
            if self.dist_left > self.dist_right:
                print(f"    -> Turning Left (L:{self.dist_left:.1f}m > R:{self.dist_right:.1f}m)")
                twist.angular.z = 0.5  # 좌회전 (양수)
            else:
                print(f"    -> Turning Right (L:{self.dist_left:.1f}m < R:{self.dist_right:.1f}m)")
                twist.angular.z = -0.5 # 우회전 (음수)
                
        # [우선순위 1] 교통 법규 준수 (Traffic Rules)
        elif is_at_stop_point:
            if traffic_light == "RED":
                # 빨간불 인식 시 정지
                print("[TRAFFIC] Stop Point detected. Signal: RED -> STOP")
                twist.linear.x = 0.0
            elif traffic_light == "GREEN":
                # 초록불 인식 시 통과
                print("[TRAFFIC] Stop Point detected. Signal: GREEN -> GO")
                twist.linear.x = 0.1
            else:
                # 스탑포인트는 있으나 신호등이 감지되지 않음 -> 통과
                print("[TRAFFIC] Stop Point detected. Signal: NONE -> PASSING")
                twist.linear.x = 0.1

        # [우선순위 2] 일반 주행 (Normal Drive)
        else:
            print("[DRIVE] Path Clear. Moving Forward.")
            twist.linear.x = 0.1  # 기본 주행 속도
            twist.angular.z = 0.0 # 직진

        # 최종 계산된 속도 명령 발행
        self.cmd_pub.publish(twist)

def main():
    rclpy.init()
    node = DecisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()