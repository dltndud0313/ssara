import time
from adafruit_servokit import ServoKit

# 1. 초기화
kit = ServoKit(channels=16)

# ---------------------------------------------------------
# [사용자 설정] 핀 번호를 여기에 입력하세요
# 몸쪽 = COXA, 몸쪽 관절 = FEMUR, 무릎 관절 = TIBIA
# ---------------------------------------------------------
# 다리 1 (기존)
L1_COXA  = 0
L1_FEMUR = 1
L1_TIBIA = 2

# 다리 2 (새로 추가된 다리 - 실제 꽂은 번호로 수정 필수!)
L2_COXA  = 3
L2_FEMUR = 4
L2_TIBIA = 6 

# ---------------------------------------------------------
# 관리 리스트 (여기에 추가하면 자동으로 모든 테스트에 포함됩니다)
# ---------------------------------------------------------
servos = [
    # 다리 1
    (L1_COXA,  "Leg1_Coxa"),
    (L1_FEMUR, "Leg1_Femur"),
    (L1_TIBIA, "Leg1_Tibia"),
    # 다리 2
    (L2_COXA,  "Leg2_Coxa"),
    (L2_FEMUR, "Leg2_Femur"),
    (L2_TIBIA, "Leg2_Tibia"),
]

# 3. 펄스 폭 설정
for pin, name in servos:
    kit.servo[pin].set_pulse_width_range(500, 2500)

print(f">>> 시스템 준비 완료. 총 {len(servos)}개의 서보를 제어합니다.")

def set_angle(pin, angle):
    kit.servo[pin].angle = angle

try:
    # -----------------------------------------------------
    # Step 0. 초기 위치 (90도)
    # -----------------------------------------------------
    print("\n[Step 0] 안전 모드: 90도 정렬 (2초 대기)")
    for pin, name in servos:
        set_angle(pin, 90)
    time.sleep(2)

    # -----------------------------------------------------
    # Step 1. 개별 관절 테스트 (순서대로 하나씩)
    # -----------------------------------------------------
    print("\n[Step 1] 개별 관절 구동 테스트")
    for pin, name in servos:
        print(f"   >>> {name} (Pin {pin}): 70 -> 110 -> 90")
        set_angle(pin, 70)
        time.sleep(0.3)
        set_angle(pin, 110)
        time.sleep(0.3)
        set_angle(pin, 90)
        time.sleep(0.3)
    
    print("\n   >>> 개별 테스트 완료. 1초 후 동시 구동 시작.")
    time.sleep(1)

    # -----------------------------------------------------
    # Step 2. 동시 기동 부하 테스트 (수정됨: 리스트 전체 동시 제어)
    # -----------------------------------------------------
    print("\n[Step 2] 동시 기동 부하 테스트 (6개 동시 구동)")
    
    # 1. 다같이 70도로 이동
    print("   >>> 모두 70도로 이동 (전류 급상승 주의!)")
    for pin, name in servos:
        set_angle(pin, 70)
    time.sleep(1.5) # 6개라 전류 안정화 시간 조금 더 줌

    # 2. 다같이 110도로 이동
    print("   >>> 모두 110도로 이동")
    for pin, name in servos:
        set_angle(pin, 110)
    time.sleep(1.5)

    # 3. 다시 90도로 복귀
    print("   >>> 모두 90도(중립) 복귀")
    for pin, name in servos:
        set_angle(pin, 90)
    time.sleep(1.0)

    print("\n[테스트 완료] 전력 공급이 6개 모터를 버텨냈습니다.")

except KeyboardInterrupt:
    print("\n테스트 강제 종료.")
    # 비상시 힘 풀기 (옵션)
    # for pin, name in servos:
    #     kit.servo[pin].angle = None 
except Exception as e:
    print(f"\n에러 발생: {e}")