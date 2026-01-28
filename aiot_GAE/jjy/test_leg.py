import time
from adafruit_servokit import ServoKit

# 1. 초기화
kit = ServoKit(channels=16)

# 2. 핀 설정 (0:몸통, 3:허벅지, 4:무릎)
COXA_PIN = 0
FEMUR_PIN = 3
TIBIA_PIN = 4

# 관리하기 쉽게 리스트로 묶음
servos = [
    (COXA_PIN, "Coxa(몸통)"),
    (FEMUR_PIN, "Femur(허벅지)"),
    (TIBIA_PIN, "Tibia(무릎)")
]

# 3. 펄스 폭 설정 (500~2500us)
for pin, name in servos:
    kit.servo[pin].set_pulse_width_range(500, 2500)

print(">>> 시스템 준비 완료.")

def set_angle(pin, angle):
    # 명령을 내리는 함수 (출력은 줄임)
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
    # Step 1. 개별 관절 테스트 (하나씩 움직임)
    # -----------------------------------------------------
    print("\n[Step 1] 개별 관절 구동 테스트")
    for pin, name in servos:
        print(f"   >>> {name} 구동: 60 -> 120 -> 90")
        set_angle(pin, 60)
        time.sleep(0.5)
        set_angle(pin, 120)
        time.sleep(0.5)
        set_angle(pin, 90)
        time.sleep(0.5)
    
    print("\n   >>> 개별 테스트 완료. 1초 후 동시 구동 시작.")
    time.sleep(1)

    # -----------------------------------------------------
    # Step 2. 동시 기동 부하 테스트 (전력 안정성 확인)
    # 파이썬 코드는 순차적이지만, 통신 속도가 빨라 사람 눈에는
    # 동시에 움직이는 것처럼 보이며 배터리에 큰 부하를 줍니다.
    # -----------------------------------------------------
    print("\n[Step 2] 동시 기동 부하 테스트 (Power Spike Check)")
    
    # 1. 다같이 60도로 이동
    print("   >>> 모두 60도로 이동 (전류 급상승 주의)")
    set_angle(COXA_PIN, 60)
    set_angle(FEMUR_PIN, 60)
    set_angle(TIBIA_PIN, 60)
    time.sleep(1.0) # 이동 완료 대기

    # 2. 다같이 120도로 이동
    print("   >>> 모두 120도로 이동")
    set_angle(COXA_PIN, 120)
    set_angle(FEMUR_PIN, 120)
    set_angle(TIBIA_PIN, 120)
    time.sleep(1.0)

    # 3. 다시 90도로 복귀
    print("   >>> 모두 90도(중립) 복귀")
    set_angle(COXA_PIN, 90)
    set_angle(FEMUR_PIN, 90)
    set_angle(TIBIA_PIN, 90)
    time.sleep(1.0)

    print("\n[테스트 완료] 이상이 없다면 전력 공급이 안정적입니다.")

except KeyboardInterrupt:
    print("\n테스트 강제 종료.")
except Exception as e:
    print(f"\n에러 발생: {e}")