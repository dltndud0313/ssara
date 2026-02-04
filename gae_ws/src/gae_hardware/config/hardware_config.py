"""
🐕 GAE Robot Hardware Configuration (v2.5)
하드웨어 핀맵, I2C 주소, 서보 모터 제어 상수를 정의합니다.

[Terminology Definition]
1. Foot     : 끝단 관절 (구 Knee)
2. Leg      : 높이 제어 관절 (구 Shoulder)
3. Shoulder : 회전 제어 관절 (구 Hip) -> [안전 주의 대상]
"""

# ---------------------------------------------------------
# 1. I2C Configuration
# ---------------------------------------------------------
I2C_BUS_SERVO = 7  # Servo Line (0x40, 0x41)
I2C_BUS_IMU   = 1  # Sensor Line (0x68)

# ---------------------------------------------------------
# 2. Device Addresses
# ---------------------------------------------------------
PCA_ADDR_FRONT = 0x41  # [Master] Front Legs
PCA_ADDR_REAR  = 0x40  # [Slave]  Rear Legs
MPU_ADDR       = 0x68  # IMU Sensor

# ---------------------------------------------------------
# 3. Servo Settings (DS3218MG)
# ---------------------------------------------------------
SERVO_MIN_PULSE = 500
SERVO_MAX_PULSE = 2500
SERVO_ACTUATION_RANGE = 180 

# ---------------------------------------------------------
# 4. Joint Mapping
# ---------------------------------------------------------
# Structure: [Foot, Leg, Shoulder]
#  - Foot    : Index 0
#  - Leg     : Index 1 (Elevation/Height)
#  - Shoulder: Index 2 (Rotation/Pivot)

PIN_MAP = {
    # --- Rear Legs (0x40) ---
    'rear-right': {
        'kit': 'rear', 
        'pins': [0, 1, 2]      # 0:foot, 1:leg, 2:shoulder
    },
    'rear-left': {
        'kit': 'rear', 
        'pins': [15, 14, 13]   # 15:foot, 14:leg, 13:shoulder
    },
    
    # --- Front Legs (0x41) ---
    'front-right': {
        'kit': 'front', 
        'pins': [0, 1, 2]      # 0:foot, 1:leg, 2:shoulder
    },
    'front-left': {
        'kit': 'front', 
        'pins': [15, 14, 13]   # 15:foot, 14:leg, 13:shoulder
    }
}

# ---------------------------------------------------------
# 5. Safety Locked Pins
# ---------------------------------------------------------
# Shoulder (Index 2, 13) joints handle high torque/rotation.
# These are locked by default in safety modes.

LOCKED_PINS = {
    'front': [2, 13],  # Front Shoulders
    'rear':  [2, 13]   # Rear Shoulders
}