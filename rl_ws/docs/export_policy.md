# `export.py`와 Sim2Real: 관측 정규화 및 ONNX 변환 분석 보고서

본 문서는 **Isaac Lab 2.3.0** 환경에서 강화학습 모델을 실제 로봇(Real Robot)에 배포하기 위해 사용하는 `export.py` 스크립트의 역할과 동작 원리를 상세히 분석합니다. 특히 시뮬레이션에서 학습된 **Policy**가 실제 환경에서도 정상적으로 동작하기 위해 필수적인 **관측 정규화(Observation Normalization)** 과정과 **ONNX 모델 구조**에 초점을 맞춥니다.

## 1. 개요 (Overview)

강화학습 훈련(Training) 과정에서 로봇은 수만 번의 시행착오를 통해 최적의 행동을 배웁니다. 이때 안정적인 학습을 위해 입력 데이터(Observation)의 스케일을 맞추는 **정규화(Normalization)**가 실시간으로 이루어집니다.

그러나 학습이 끝난 후 생성된 체크포인트 파일(`model_*.pt`)은 단순히 신경망의 가중치(Weight) 뿐만 아니라, 정규화에 사용된 통계값(평균, 분산)을 별도로 포함하고 있습니다. **`export.py`는 이 통계값을 신경망 앞단에 계산식으로 통합(Fusing)하여, 별도의 전처리 없이도 로봇의 센서 원본 데이터(Raw Data)를 바로 입력받을 수 있는 모델을 생성합니다.**

---

## 2. 관측 정규화 (Observation Normalization)

강화학습, 특히 PPO(Proximal Policy Optimization) 알고리즘에서는 입력값의 범위가 일정하지 않으면(예: 관절 각도는 -3.14~3.14, IMU 가속도는 -10~10 등) 학습이 불안정해집니다. 이를 방지하기 위해 **Running Mean(이동 평균)**과 **Running Variance(이동 분산)**을 사용하여 정규화를 수행합니다.

### 2.1 학습 단계 (Training)
학습 중에는 매 스텝마다 들어오는 Observation 데이터 $x$에 대해 통계값을 업데이트하고, 다음 식을 통해 정규화된 값 $\hat{x}$를 신경망에 전달합니다.

$$ \hat{x} = \mathrm{clip}\left(\frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}}, -5.0, 5.0\right) $$

*   $\mu$ (Mean): 관측값의 평균 (계속 업데이트됨)
*   $\sigma^2$ (Variance): 관측값의 분산 (계속 업데이트됨)
*   $\epsilon$: 0으로 나누는 것을 방지하기 위한 작은 상수 (보통 $1e-5$)

### 2.2 배포 단계 (Deployment via `export.py`)
학습이 완료된 시점의 $\mu$와 $\sigma^2$는 고정됩니다. `export.py`는 이 고정된 값들을 추출하여, **입력 데이터가 들어오자마자 동일한 수식으로 변환하는 연산 레이어를 신경망의 첫 번째 층으로 추가**합니다.

> **Why it matters:**
> 만약 정규화 정보 없이 Actor 네트워크($\pi$)만 가져가면, 실제 로봇 센서에서 들어온 $x$값이 정규화된 $\hat{x}$와는 스케일이 완전히 다르기 때문에 로봇이 엉뚱한 행동을 하게 됩니다.

---

## 3. ONNX 모델 구조 및 동작

`export.py`를 통해 생성된 `.onnx` 파일은 다음과 같은 내부 구조를 가집니다.

```mermaid
graph LR
    A[Robot Sensors<br/>(Raw Observation)] --> B[Normalization Layer<br/>(x - mean / std)]
    B --> C[Clip Layer<br/>(-5.0 ~ 5.0)]
    C --> D[Actor Network<br/>(MLP)]
    D --> E[Actuator Commands<br/>(Raw Actions)]
```

### 3.1 Input / Output
*   **Input (`obs`):** 로봇의 센서에서 읽어온 가공되지 않은 물리량 (Raw Data).
    *   예: `[선속도(3), 각속도(3), 중력벡터(3), 목표속도(3), 이전행동(12)]` 등.
*   **Output (`actions`):** 로봇의 관절 제어기에 들어갈 명령값.
    *   보통 `Action Scale`을 곱하고 `Default Joint Pos`를 더하여 최종 목표 각도로 변환합니다.

### 3.2 `controlled_by_model.py`와의 관계
사용자가 작성한 `scripts/sim2real/controlled_by_model.py` 코드를 보면, 별도의 정규화 로직이 없습니다.

```python
# controlled_by_model.py 발췌
obs_tensor = torch.from_numpy(obs_np).unsqueeze(0).to(self.device)

# 3. 모델 추론 (Inference)
with torch.no_grad():
    # 여기서 모델은 이미 정규화 레이어를 포함하고 있음!
    actions_tensor = self.model(obs_tensor)
```

이 코드가 정상 작동하는 이유는 **로드한 모델(policy.pt 또는 policy.onnx) 내부에 이미 정규화 연산이 "구워져(Baked in)" 있기 때문**입니다. 따라서 사용자는 로봇의 센서값을 그대로 벡터로 만들어 넣어주기만 하면 됩니다.

---

## 4. `export.py` 사용법 (Isaac Lab 2.3.0)

Isaac Lab 2.3.0에서는 `export.py`가 `rsl_rl` 라이브러리의 익스포터를 래핑하고 있습니다.

### 4.1 기본 명령어
```bash
# Isaac Lab 디렉토리로 이동
cd ~/IsaacLab

# Export 실행
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/export.py \
    --task=Isaac-Velocity-Flat-NoSensor-Spot-Micro-v0 \
    --load_run [날짜_시간] \
    --checkpoint [모델파일.pt]
```

### 4.2 주요 인자 설명
*   **`--task`**: 환경 설정을 로드합니다. (Observation/Action 차원 확인용)
*   **`--load_run`**: `logs/rsl_rl/` 내의 특정 실험 폴더를 지정합니다.
*   **`--checkpoint`**: 변환할 `.pt` 파일을 지정합니다. 지정하지 않으면 가장 최신 모델을 사용합니다.
*   **`--onnx_args`**: ONNX opset 버전 등을 지정할 수 있습니다. (기본값 사용 권장)

### 4.3 결과물
실행이 완료되면 해당 실험 로그 폴더 내 `exported` 디렉토리가 생성됩니다.
*   `policy.onnx`: ONNX 런타임용 모델 (C++, Python, TensortRT 등 호환)
*   `policy.pt`: JIT 컴파일된 PyTorch 모델 (Python 전용, `torch.jit.load`로 사용)

---

## 5. 결론 및 Sim2Real 가이드

1.  **항상 `export.py`를 사용하세요.**
    *   학습된 `model_*.pt` 파일을 직접 로드해서 추론하려 하지 마십시오. 정규화 통계가 적용되지 않아 실패할 확률이 매우 높습니다.
2.  **입력 데이터 순서를 맞추세요.**
    *   `env_cfg.py`의 `observations.policy.concatenate_terms` 순서와 실제 로봇 코드의 벡터 조립 순서가 정확히 일치해야 합니다.
3.  **Action Scale을 확인하세요.**
    *   모델이 뱉어내는 값은 보통 작은 범위(예: -1.0 ~ 1.0)의 값입니다. 이를 실제 모터 각도로 변환할 때 사용하는 `action_scale` (예: 0.25 또는 0.5)이 시뮬레이션 설정과 동일해야 합니다.
