- gain tuner: tools - robotics - asset editor - gain tuner
	- 뭘 봐야하는거지? command, observed 그래프?
- visual, collision이 child로서 잘 존재하는지 봐야함
- articulation Root - 이건 로봇팔이라 설정하는 듯
- physics inspector
- collider
	- convex hull vs convex decomposition

## 5. Import Your Robots From URDF to USD - Isaac Sim Tutorial

**원본 링크**: [https://www.youtube.com/watch?v=AMfEtZ4hyLY](https://www.youtube.com/watch?v=AMfEtZ4hyLY)

### Determining Values for Real Robots

**Documentation**: Tuning Joint Drive Gains — Isaac Sim Documentation

실제 로봇에 대한 최적의 Stiffness와 Damping 값을 결정하는 방법은 여러 가지가 있습니다:

*   **제조업체 사양 참조**: 가능한 경우 제조사에서 제공하는 값을 사용합니다.
*   **시스템 식별 기법 사용**: 주파수 응답 분석(Frequency Response Analysis) 등.
*   **Step Input 적용**: 진동 주파수와 감쇠를 측정합니다.
*   **반복적인 실험적 테스트**: 보수적인 값에서 시작하여 점차 조절합니다.

예를 들어, **SO-ARM100** 로봇의 경우 제조업체 사양이 없으며 제공된 URDF의 관성 값 정확도가 불확실할 수 있습니다. 이러한 경우:

진동 분석이나 주파수 스윕 테스트와 같은 공식적인 접근 방식은 정확한 값을 제공하지만, 전문 장비가 필요하고 실용적인 시행착오(Trial and Error) 방식보다 훨씬 많은 시간이 소요될 수 있습니다. 많은 애플리케이션에서 보수적인 값으로 시작하는 체계적인 시행착오 접근 방식이 더 효율적입니다.

그러나 **Domain randomization**을 활용하면 이런 값들이 매우 정확할 필요는 없다.
키워드: closing sim to real gap