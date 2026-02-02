import time
from adafruit_servokit import ServoKit

# ---------------------------------------------------------
# [사용자 설정] 연결된 모든 서보의 핀 번호를 여기에 적으세요.
# 순서는 상관없습니다. 사용 중인 핀 번호만 나열하면 됩니다.
# ---------------------------------------------------------
SERVO_PINS = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
]

def reset_all_servos():
    # 1. PCA9685 연결
    try:
        kit = ServoKit(channels=16)
    except Exception as e:
        print(f"ERROR: PCA9685 보드를 찾을 수 없습니다.\n{e}")
        return

    print(f"\n>>> 총 {len(SERVO_PINS)}개의 서보를 90도(중립)로 초기화합니다.")

    # 2. 서보 설정 및 이동
    for pin in SERVO_PINS:
        # 핀 번호 유효성 체크 (0~15)
        if 0 <= pin <= 15:
            # 펄스 폭 설정 (필수: 이게 없으면 90도 위치가 틀어짐)
            kit.servo[pin].set_pulse_width_range(500, 2500)
            
            # 90도로 이동
            kit.servo[pin].angle = 90
            print(f" - Pin {pin}: 90도 설정 완료")
            
            # 전력 피크 방지를 위해 아주 짧은 대기 (모터가 많아질수록 중요)
            time.sleep(0.1)
        else:
            print(f" [경고] 잘못된 핀 번호입니다: {pin}")

    print("\n>>> 초기화 완료. 모든 관절이 90도를 유지합니다.")
    print(">>> (프로그램이 종료되어도 서보는 힘을 유지합니다)")

if __name__ == "__main__":
    reset_all_servos()