현재 파일(

flat_env_recent.py
)에 설정된 50Hz 시뮬레이션 환경에 실제 로봇을 맞추기 위한 값입니다.

시뮬레이션 코드가 decimation = 4 (50Hz)로 설정되어 있으므로, 실제 로봇 센서도 50Hz로 데이터를 뽑아야 1:1 매칭이 됩니다.

1. SMPLRT_DIV (샘플 레이트 분주비)
추천 값: 19 (0x13)
이유:
현재 시뮬레이션 제어 주기: $0.005s \times 4 = 0.02s$ (50 Hz)
목표: Real Robot도 50 Hz로 설정
계산: $50 Hz = \frac{1000 Hz}{1 + SMPLRT_DIV} \rightarrow SMPLRT_DIV = 19$
2. DLPF_CFG (디지털 로우패스 필터)
추천 값: 4 (21Hz 대역폭) 또는 3 (44Hz 대역폭)
이유:
제어 주기가 50Hz로 느려졌으므로, 필터 대역폭도 더 낮춰야 앨리어싱(Aliasing)을 막을 수 있습니다.
설정 4 (21Hz): 50Hz 샘플링에 가장 적합한 필터 (Nyquist Frequency 25Hz 이하). 데이터가 매우 부드럽고 안정적이지만 지연 시간(8.5ms)이 조금 있습니다.
설정 3 (44Hz): 반응은 더 빠르지만(4.9ms), 50Hz 주기에서는 노이즈가 튈 수 있습니다.
3. 요약 (제안)
안정적인 심-리얼(Sim-to-Real) 매칭을 원하신다면 아래 조합을 추천합니다.

설정 항목	값 (10진수)	값 (16진수)	설명
SMPLRT_DIV	19	0x13	50 Hz 출력 (Sim 제어 주기와 일치)
DLPF_CFG	4	0x04	21 Hz 필터 (느린 주기에 맞춰 노이즈 제거 강화)

isaac sim gui에서는 값을 다음과 같이 수정하면 된다.
1. Angular Velocity Filter Width (Gyro Bandwidth)
값: 42 Hz
설명: DLPF_CFG=3일 때 자이로스코프의 대역폭은 42Hz가 되며, 지연 시간(Delay)은 약 4.8ms입니다.
2. Linear Acceleration Filter Width (Accel Bandwidth)
값: 44 Hz
설명: DLPF_CFG=3일 때 가속도계의 대역폭은 44Hz가 되며, 지연 시간(Delay)은 약 4.9ms입니다.
3. Sensor Period (Sample Period)
값: 0.01 seconds (10ms)
계산 과정:
DLPF가 켜져 있으므로(3), 내부 Gyro Rate는 **1kHz (1000Hz)**가 됩니다.
Sample Rate = $1000 / (1 + 9) = 100Hz$
Period = $1 / 100Hz = 0.01s$
요약 (Isaac Sim 등의 Config 입력용)
angular_velocity_filter_width: 42
linear_acceleration_filter_width: 44
sensor_period: 0.01