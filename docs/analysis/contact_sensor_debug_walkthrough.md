# 커스텀 4족 보행 로봇 접촉 센서 디버깅

## 문제 상황
`activate_contact_sensors=True`로 설정했음에도 불구하고 `RuntimeError: Sensor at path '...' could not find any bodies with contact reporter API.` 오류와 함께 학습이 실패했습니다.
이로 인해 다음 기능들을 사용할 수 없었습니다:
- `self.scene.contact_forces` (센서)
- `self.rewards.feet_air_time` (센서 의존)
- `self.terminations.base_contact` (몸통 접촉 의존)

## 원인
1.  **API 누락**: `quadruped.usd` 에셋(또는 스폰된 인스턴스)의 관련 바디(`trunk` 및 종아리)에 `PhysxContactReportAPI`가 적용되지 않았거나, 자동 적용이 실패했습니다.
    - *해결*: `add_contact_api.py`를 사용하여 `PhysxContactReportAPI`를 수동으로 적용했습니다.
2.  **계층 구조 불일치**: 설정에서는 로봇 바디가 스폰된 프림의 직계 자식일 것으로 예상했으나(`.../Robot/FL_calf`), 실제 씬을 검사한 결과 중간에 Xform이 존재했습니다: `.../Robot/quadruped_robot/FL_calf`.
    - *증거*: `.../env_0/Robot` 아래에서 `[DEBUG] Child: quadruped_robot Type: Xform` 발견.
3.  **센서 경로 로직**: `ContactSensor`는 경로 분할 로직(`rsplit("/", 1)`)을 사용하는데, 단순 glob 사용 시 예상치 못한 중간 디렉토리를 순회하지 못했습니다.
4.  **종료 조건 불일치**: `base_contact` 종료 조건은 `trunk`를 필요로 했으나, 센서는 처음에 `.*_calf`만 찾도록 설정되어 있어 정책이 `trunk`를 요청할 때 검증 오류가 발생했습니다.

## 해결 방법

### 1. USD 패치
`quadruped.usd` 파일의 `trunk` 및 `.*_calf` 프림에 `PhysxContactReportAPI`를 적용했습니다.

### 2. 정규식 업데이트
중간 `quadruped_robot` 디렉토리를 포함하고 Contact API가 있는 모든 바디(trunk + 종아리)를 캡처하도록 `env_cfg.py`의 명시적 경로를 업데이트했습니다.

**파일:** `scripts/custom_quadruped_isaac/env_cfg.py`
```python
# 변경 전
self.scene.contact_forces.prim_path = "{ENV_REGEX_NS}/Robot/.*" # 또는 ".*_calf"

# 변경 후
self.scene.contact_forces.prim_path = "{ENV_REGEX_NS}/Robot/quadruped_robot/.*"
```

이 정규식 `.../quadruped_robot/.*`은 다음을 매칭합니다:
- `.../quadruped_robot/trunk`
- `.../quadruped_robot/FL_calf` (등등)
- `ContactSensor`는 이 목록을 `PhysxContactReportAPI`가 있는 바디만 포함하도록 자동으로 필터링합니다. 우리는 trunk와 종아리만 패치했으므로(hip/thigh에도 있을 수 있지만 괜찮음), 올바른 센서 뷰가 생성됩니다.

## 검증
이제 학습 루프가 성공적으로 실행됩니다(`Learning iteration 1/40000`).
메트릭을 통해 정책이 활성화되었음을 확인했습니다:
- `Episode_Reward/feet_air_time`: 데이터 생성됨 (0이 아니며 변화함).
- `Episode_Termination/base_contact`: 활성화됨 (0.0000).

## 생성/수정된 파일
- `scripts/custom_quadruped_isaac/env_cfg.py`: 센서 경로 업데이트.
- `patch_sensor.py`: Isaac Lab 센서 로직 디버깅용 유틸리티 (삭제 가능).
- `add_contact_api.py`: USD 패치용 유틸리티.
- `inspect_usd.py`: USD 구조 검증용 유틸리티.
