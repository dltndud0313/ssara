import time
import board
import busio
import adafruit_mpu6050

# Jetson Orin Nano의 i2c-1 (SCL=Pin 28, SDA=Pin 27)
i2c = busio.I2C(board.SCL_1, board.SDA_1)
mpu = adafruit_mpu6050.MPU6050(i2c)

print("IMU 데이터 확인 시작 (Ctrl+C로 종료)")
print("-------------------------------------------------------------")
print("가속도(Accel) - 단위: m/s^2 | 자이로(Gyro) - 단위: rad/s")
print("-------------------------------------------------------------")

while True:
    accel = mpu.acceleration
    gyro = mpu.gyro
    
    # 소수점 2자리까지 출력
    print(f"Accel X:{accel[0]:.2f} Y:{accel[1]:.2f} Z:{accel[2]:.2f} || Gyro X:{gyro[0]:.2f} Y:{gyro[1]:.2f} Z:{gyro[2]:.2f}")
    time.sleep(0.5)