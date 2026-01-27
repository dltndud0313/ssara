# Battery
## Connected devices
> 배터리는 아래 장치들에 전력을 공급한다.
- jetson orin nano
- sensors: HC-SR04, MPU-6050, PCA9685
- DS3218MG pro * 12
- Orbbec Astra Pro 3D 카메라

## Validity
| 구분        | 요구사항                                                                                    |
| --------- | --------------------------------------------------------------------------------------- |
| 전압        | 배터리(예: 2S~3S LiPo)를 DC-DC로 분리해 서보 레일 6V, Jetson/센서/카메라 5V 안정화                           |
| 전류 - 서보   | DS3218MG pro 12개 스톨 가정 2~2.5A/ea -> 피크 약 24~30A @6V. 서보용 벅컨 연속 15A+, 피크 30A+ 권장         |
| 전류 - 시스템  | Jetson Orin Nano + Orbbec Astra Pro + 센서: 약 20~25W -> 5V 기준 4~5A (배터리 측 3S 기준 약 2~2.5A) |
| 전류 - 총 피크 | 서보 30A + 논서보 여유 3A -> 순간 33A 이상 공급 가능한 배터리/배선/BMS 필요                                    |
| 배터리 연속 방전 | 서보 평균 0.5A/ea 가정 시 6A + 시스템 3A ~ 9A -> 여유 포함 15A급 이상 권장                                 |
| 배터리 피크 방전 | 33A 이상 (3S 5600mAh 100C는 여유 충분, 병목은 DC-DC·커넥터·배선)                                       |
| BMS 조건    | 차단 전류가 피크보다 높고, 저전압 컷오프가 2S/3S에 맞는 팩 사용할 것                                              |
| 예상 구동 시간  | 3S 5600mAh(약 62Wh) 기준, 평균 10A@11.1V 소비 시 `t ~ 0.56h`(약 34분). 부하 증가 시 비례 단축              |

## 1. 후보 모델
> mike version, florian wilk version, road balance version 셋 모두 7.4v 배터리를 사용
1. [TERANTY 3S 5600mAh 11.4V 100C](https://ko.aliexpress.com/item/1005010705840139.html?spm=a2g0o.productlist.main.1.60ab5aad8Hv1PX&algo_pvid=070da2e4-ae3a-4383-94df-380ad06c4669&algo_exp_id=070da2e4-ae3a-4383-94df-380ad06c4669-0&pdp_ext_f=%7B%22order%22%3A%224%22%2C%22eval%22%3A%221%22%2C%22fromPage%22%3A%22search%22%7D&pdp_npi=6%40dis%21KRW%2158596%2133400%21%21%21272.97%21155.59%21%402101246417681861460738245ec19e%2112000053251340883%21sea%21KR%216231451114%21X%211%210%21n_tag%3A-29919%3Bd%3A19dff378%3Bm03_new_user%3A-29895&curPageLogUid=cEfwJECzNLJu&utparam-url=scene%3Asearch%7Cquery_from%3A%7Cx_object_id%3A1005010705840139%7C_p_origin_prod%3A)

# 참고자료
## datasheets
- Jetson Orin Nano Developer Kit: https://d29g4g2dyqv443.cloudfront.net/sites/default/files/Jetson_Orin_Nano_Developer_Kit_RG_0.pdf
- HC-SR04 초음파 센서: https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf
- MPU-6050 IMU: https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf
- Rocker 스위치 RL2-321: https://www.edcon-components.com/Webside/PDFEA/RL2_3.pdf
- XL4016 DC-DC 컨버터: https://datasheet.lcsc.com/szlcsc/1811021511_XI-LAN-DCSHANGHAI-XI-LIAN-XL4016_C105450.pdf
- LM2596 DC-DC 컨버터: https://www.ti.com/lit/ds/symlink/lm2596.pdf
- PCA9685 PWM 서보 드라이버: https://cdn-shop.adafruit.com/datasheets/PCA9685.pdf
- DS3218MG 서보 모터: https://www.dsservo.com/d_file/DS3218%20datasheet.pdf
- Orbbec Astra Pro 3D 카메라: https://www.mybotshop.de/Datasheet/Orbbec_Astra_Pro_Final.pdf
- 커넥터류, 점퍼케이블, 수축튜브는 충민이 꺼 사용
- 서포트는 SSAFY 제공 키트에 포함

## 2. Isaac Sim Simulation Parameters & Hardware Validity Analysis

### 2.1 PCA9685 Driver Constraints (CRITICAL)
> **Constraint**: Standard PCA9685 Breakout Boards have thin power traces (V+ to GND) typically rated for **3A continuous (max ~10A peak)**.
> **Requirement**: 12 x DS3218MG servos @ Stall Draw ~30A peak (2.5A/ea).
> **Conclusion**: Routing Servo Power through the PCA9685 board is **INVALID** (Risk of trace failure/fire). Power must be routed via external bus-bars or a dedicated power distribution board, using PCA9685 for Signal (PWM) only.

### 2.2 Parameter Calculation
| Scenario | Conditions | `maxForce`<br>(Nm) | `maxActuatorVelocity`<br>(deg/s) | `speedEffortGradient`<br>(deg/s/Nm) | `velocityDependentResistance`<br>(Nm·s/deg) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Ideal (Recommended)** | Power connected **Externally** (Direct from Buck) | **2.17** | **551** | **254** | **0.00394** |
| **Board Limited (Unsafe)** | Power via **PCA9685 Board** (Assuming 10A Total Limit) | ~0.72* | 551 | 765 | 0.0013 |

> (*) `maxForce` limited by board current share (approx 0.83A/servo vs 2.5A req).

### 2.3 Updated Simulation Values (Use 'Ideal' for correct Sim)
> 시뮬레이션에서는 로봇이 이상적으로 배선되었다고 가정하고 **Ideal** 값을 사용하되, 실제 하드웨어 제작 시 **외부 전원 배선**이 필수적임을 명심해야 합니다.

| Parameter | Value | Unit | Description |
| --- | --- | --- | --- |
| `maxForce` | **2.17** | Nm | Stall Torque @ 6V |
| `maxActuatorVelocity` | **551** | deg/s | No-load Speed @ 6V (0.109s/60°) |
| `speedEffortGradient` | **254** | deg/s/Nm | Ideal Response |
| `velocityDependentResistance` | **0.00394** | Nm·s/deg | Damping |