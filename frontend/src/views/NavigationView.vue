<template>
  <div class="navigation-view">
    <header class="header">
      <button class="back-btn" @click="$router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
      <h1 class="header-title">위치간 이동</h1>
      <button class="reset-btn" @click="resetNavigation" v-if="startPoint || endPoint">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="23 4 23 10 17 10"/>
          <polyline points="1 20 1 14 7 14"/>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
        </svg>
      </button>
      <div v-else class="header-spacer"></div>
    </header>

    <main class="content">
      <!-- 경로 설정 카드 -->
      <section class="route-card">
        <div class="route-item" @click="selectingPoint = 'start'">
          <div class="route-icon start">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="8"/>
            </svg>
          </div>
          <div class="route-info">
            <span class="route-label">출발지</span>
            <span class="route-value" :class="{ placeholder: !startPoint }">
              {{ startPoint ? startPoint.name : '지도에서 선택하세요' }}
            </span>
          </div>
          <button class="current-location-btn" @click.stop="setCurrentAsStart" title="현재 위치">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
          </button>
        </div>

        <div class="route-divider">
          <div class="divider-line"></div>
          <button class="swap-btn" @click="swapPoints" :disabled="!startPoint || !endPoint">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="17 1 21 5 17 9"/>
              <path d="M3 11V9a4 4 0 0 1 4-4h14"/>
              <polyline points="7 23 3 19 7 15"/>
              <path d="M21 13v2a4 4 0 0 1-4 4H3"/>
            </svg>
          </button>
          <div class="divider-line"></div>
        </div>

        <div class="route-item" @click="selectingPoint = 'end'">
          <div class="route-icon end">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
          </div>
          <div class="route-info">
            <span class="route-label">도착지</span>
            <span class="route-value" :class="{ placeholder: !endPoint }">
              {{ endPoint ? endPoint.name : '지도에서 선택하세요' }}
            </span>
          </div>
        </div>
      </section>

      <!-- 선택 모드 안내 -->
      <div class="selection-guide" v-if="selectingPoint">
        <div class="guide-content">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          <span>지도에서 {{ selectingPoint === 'start' ? '출발지' : '도착지' }}를 선택하세요</span>
        </div>
        <button class="cancel-btn" @click="selectingPoint = null">취소</button>
      </div>

      <!-- 지도 영역 -->
      <section class="map-section">
        <div class="map-container" ref="mapContainer">
          <div ref="kakaoMapRef" class="kakao-map"></div>

          <!-- 지도 컨트롤 -->
          <div class="map-controls">
            <button class="map-control-btn" @click="zoomIn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
            </button>
            <button class="map-control-btn" @click="zoomOut">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
            </button>
            <button class="map-control-btn" @click="moveToCurrentLocation">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="3 11 22 2 13 21 11 13 3 11"/>
              </svg>
            </button>
          </div>
        </div>
      </section>

      <!-- 프리셋 위치 -->
      <section class="preset-section">
        <h3 class="section-title">자주 가는 위치</h3>
        <div class="preset-list">
          <button
            class="preset-item"
            v-for="preset in presetLocations"
            :key="preset.id"
            @click="selectPreset(preset)"
          >
            <div class="preset-icon" :style="{ background: preset.color }">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
            </div>
            <span class="preset-name">{{ preset.name }}</span>
          </button>
        </div>
      </section>

      <!-- 경로 정보 -->
      <section class="route-info-section" v-if="routeInfo">
        <h3 class="section-title">경로 정보</h3>
        <div class="route-info-card">
          <div class="route-stat">
            <span class="stat-value">{{ routeInfo.distance }}</span>
            <span class="stat-label">예상 거리</span>
          </div>
          <div class="route-stat">
            <span class="stat-value">{{ routeInfo.duration }}</span>
            <span class="stat-label">예상 시간</span>
          </div>
        </div>
      </section>

      <div class="bottom-spacer"></div>
    </main>

    <!-- 이동 시작 버튼 -->
    <div class="bottom-action" v-if="startPoint && endPoint">
      <button class="start-navigation-btn" @click="startNavigation">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="3 11 22 2 13 21 11 13 3 11"/>
        </svg>
        <span>이동 시작</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useRobotStore } from '@/stores/robotStore';

const robotStore = useRobotStore();

// 지도 관련
const mapContainer = ref(null);
const kakaoMapRef = ref(null);
let kakaoMap = null;
let startMarker = null;
let endMarker = null;
let polyline = null;

// 경로 설정
const startPoint = ref(null);
const endPoint = ref(null);
const selectingPoint = ref(null);
const routeInfo = ref(null);

// VSLAM 좌표 설정
const coordConfig = reactive({
  originLat: 35.20527,
  originLng: 126.8117,
  heading: 0
});

// 프리셋 위치
const presetLocations = ref([
  { id: 1, name: '거실', lat: 35.20530, lng: 126.8118, color: '#3182f6' },
  { id: 2, name: '침실', lat: 35.20525, lng: 126.8116, color: '#20c997' },
  { id: 3, name: '주방', lat: 35.20528, lng: 126.8119, color: '#F59E0B' },
  { id: 4, name: '현관', lat: 35.20522, lng: 126.8115, color: '#EF4444' },
]);

// 카카오맵 SDK 로드
const loadKakaoMapSdk = () => {
  return new Promise((resolve, reject) => {
    if (window.kakao && window.kakao.maps) {
      resolve();
      return;
    }
    const apiKey = import.meta.env.VITE_KAKAO_MAP_API_KEY;
    if (!apiKey) {
      reject(new Error('카카오맵 API 키가 설정되지 않았습니다.'));
      return;
    }
    const script = document.createElement('script');
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&libraries=services&autoload=false`;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('카카오맵 SDK 로드 실패'));
    document.head.appendChild(script);
  });
};

// 지도 초기화
const initMap = async () => {
  try {
    await loadKakaoMapSdk();
    window.kakao.maps.load(() => {
      createMap();
    });
  } catch (error) {
    console.error('카카오맵 초기화 실패:', error);
  }
};

const createMap = () => {
  const container = kakaoMapRef.value;
  if (!container) return;

  const options = {
    center: new window.kakao.maps.LatLng(coordConfig.originLat, coordConfig.originLng),
    level: 2
  };

  kakaoMap = new window.kakao.maps.Map(container, options);

  // 지도 클릭 이벤트
  window.kakao.maps.event.addListener(kakaoMap, 'click', (mouseEvent) => {
    if (!selectingPoint.value) return;

    const latlng = mouseEvent.latLng;
    const point = {
      lat: latlng.getLat(),
      lng: latlng.getLng(),
      name: `선택한 위치`
    };

    // 역지오코딩으로 주소 가져오기
    const geocoder = new window.kakao.maps.services.Geocoder();
    geocoder.coord2Address(latlng.getLng(), latlng.getLat(), (result, status) => {
      if (status === window.kakao.maps.services.Status.OK) {
        const address = result[0];
        if (address.road_address) {
          point.name = address.road_address.building_name || address.road_address.road_name;
        } else if (address.address) {
          point.name = address.address.region_3depth_name;
        }
      }

      if (selectingPoint.value === 'start') {
        setStartPoint(point);
      } else if (selectingPoint.value === 'end') {
        setEndPoint(point);
      }
      selectingPoint.value = null;
    });
  });

  // 현재 로봇 위치 표시
  addRobotMarker();
};

// 로봇 마커 추가
const addRobotMarker = () => {
  if (!kakaoMap) return;

  const robotPosition = new window.kakao.maps.LatLng(coordConfig.originLat, coordConfig.originLng);
  const markerContent = `
    <div style="width: 24px; height: 24px; background: #3182f6; border: 3px solid white; border-radius: 50%; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>
  `;

  new window.kakao.maps.CustomOverlay({
    position: robotPosition,
    content: markerContent,
    yAnchor: 0.5,
    xAnchor: 0.5,
    map: kakaoMap
  });
};

// 시작점 설정
const setStartPoint = (point) => {
  startPoint.value = point;

  if (startMarker) {
    startMarker.setMap(null);
  }

  const position = new window.kakao.maps.LatLng(point.lat, point.lng);
  const markerContent = `
    <div style="display: flex; flex-direction: column; align-items: center;">
      <div style="width: 32px; height: 32px; background: #20c997; border: 3px solid white; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="white"><circle cx="12" cy="12" r="6"/></svg>
      </div>
      <div style="margin-top: 4px; padding: 4px 8px; background: #20c997; color: white; border-radius: 4px; font-size: 11px; font-weight: 600; white-space: nowrap;">출발</div>
    </div>
  `;

  startMarker = new window.kakao.maps.CustomOverlay({
    position: position,
    content: markerContent,
    yAnchor: 1,
    xAnchor: 0.5,
    map: kakaoMap
  });

  updateRoute();
};

// 도착점 설정
const setEndPoint = (point) => {
  endPoint.value = point;

  if (endMarker) {
    endMarker.setMap(null);
  }

  const position = new window.kakao.maps.LatLng(point.lat, point.lng);
  const markerContent = `
    <div style="display: flex; flex-direction: column; align-items: center;">
      <div style="width: 32px; height: 32px; background: #EF4444; border: 3px solid white; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/></svg>
      </div>
      <div style="margin-top: 4px; padding: 4px 8px; background: #EF4444; color: white; border-radius: 4px; font-size: 11px; font-weight: 600; white-space: nowrap;">도착</div>
    </div>
  `;

  endMarker = new window.kakao.maps.CustomOverlay({
    position: position,
    content: markerContent,
    yAnchor: 1,
    xAnchor: 0.5,
    map: kakaoMap
  });

  updateRoute();
};

// 경로 업데이트
const updateRoute = () => {
  if (!startPoint.value || !endPoint.value || !kakaoMap) return;

  // 기존 경로선 제거
  if (polyline) {
    polyline.setMap(null);
  }

  const path = [
    new window.kakao.maps.LatLng(startPoint.value.lat, startPoint.value.lng),
    new window.kakao.maps.LatLng(endPoint.value.lat, endPoint.value.lng)
  ];

  polyline = new window.kakao.maps.Polyline({
    path: path,
    strokeWeight: 5,
    strokeColor: '#3182f6',
    strokeOpacity: 0.8,
    strokeStyle: 'solid'
  });

  polyline.setMap(kakaoMap);

  // 경로 정보 계산
  const distance = calculateDistance(startPoint.value, endPoint.value);
  const duration = Math.ceil(distance / 0.5); // 로봇 속도 0.5m/s 가정

  routeInfo.value = {
    distance: distance < 1000 ? `${distance.toFixed(0)}m` : `${(distance / 1000).toFixed(1)}km`,
    duration: duration < 60 ? `${duration}초` : `${Math.ceil(duration / 60)}분`
  };

  // 경로가 보이도록 지도 범위 조정
  const bounds = new window.kakao.maps.LatLngBounds();
  bounds.extend(path[0]);
  bounds.extend(path[1]);
  kakaoMap.setBounds(bounds);
};

// 거리 계산 (Haversine formula)
const calculateDistance = (point1, point2) => {
  const R = 6371000; // 지구 반지름 (m)
  const dLat = (point2.lat - point1.lat) * Math.PI / 180;
  const dLng = (point2.lng - point1.lng) * Math.PI / 180;
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(point1.lat * Math.PI / 180) * Math.cos(point2.lat * Math.PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
};

// 현재 위치를 출발지로 설정
const setCurrentAsStart = () => {
  const point = {
    lat: coordConfig.originLat,
    lng: coordConfig.originLng,
    name: '현재 위치'
  };
  setStartPoint(point);
};

// 출발/도착 교환
const swapPoints = () => {
  if (!startPoint.value || !endPoint.value) return;

  const temp = { ...startPoint.value };
  setStartPoint({ ...endPoint.value });
  setEndPoint(temp);
};

// 프리셋 선택
const selectPreset = (preset) => {
  const point = {
    lat: preset.lat,
    lng: preset.lng,
    name: preset.name
  };

  if (!startPoint.value) {
    setStartPoint(point);
  } else if (!endPoint.value) {
    setEndPoint(point);
  } else {
    // 둘 다 있으면 도착지 변경
    setEndPoint(point);
  }
};

// 초기화
const resetNavigation = () => {
  startPoint.value = null;
  endPoint.value = null;
  routeInfo.value = null;
  selectingPoint.value = null;

  if (startMarker) {
    startMarker.setMap(null);
    startMarker = null;
  }
  if (endMarker) {
    endMarker.setMap(null);
    endMarker = null;
  }
  if (polyline) {
    polyline.setMap(null);
    polyline = null;
  }

  if (kakaoMap) {
    kakaoMap.setCenter(new window.kakao.maps.LatLng(coordConfig.originLat, coordConfig.originLng));
    kakaoMap.setLevel(2);
  }
};

// 지도 컨트롤
const zoomIn = () => {
  if (kakaoMap) kakaoMap.setLevel(kakaoMap.getLevel() - 1);
};

const zoomOut = () => {
  if (kakaoMap) kakaoMap.setLevel(kakaoMap.getLevel() + 1);
};

const moveToCurrentLocation = () => {
  if (kakaoMap) {
    kakaoMap.setCenter(new window.kakao.maps.LatLng(coordConfig.originLat, coordConfig.originLng));
  }
};

// 이동 시작
const startNavigation = () => {
  if (!startPoint.value || !endPoint.value) return;

  // 실제로는 로봇에 이동 명령을 보내야 함
  alert(`로봇이 "${startPoint.value.name}"에서 "${endPoint.value.name}"(으)로 이동을 시작합니다.`);

  // TODO: robotStore를 통해 이동 명령 전송
  // robotStore.sendNavigationCommand(startPoint.value, endPoint.value);
};

onMounted(() => {
  robotStore.connectWebSocket();
  nextTick(() => {
    initMap();
  });
});

onUnmounted(() => {
  robotStore.disconnectWebSocket();
});
</script>

<style scoped>
.navigation-view {
  min-height: 100vh;
  background: #f2f4f6;
  padding-bottom: 100px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
}

.back-btn, .reset-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7684;
}

.reset-btn:hover {
  background: #f2f4f6;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #191f28;
}

.header-spacer {
  width: 40px;
}

.content {
  padding: 16px;
}

/* 경로 설정 카드 */
.route-card {
  background: #fff;
  border-radius: 20px;
  padding: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.route-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.route-item:hover {
  background: #f8f9fa;
}

.route-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.route-icon.start {
  background: #e6f7f2;
  color: #20c997;
}

.route-icon.end {
  background: #fee2e2;
  color: #EF4444;
}

.route-info {
  flex: 1;
  min-width: 0;
}

.route-label {
  display: block;
  font-size: 12px;
  color: #8b95a1;
  margin-bottom: 2px;
}

.route-value {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: #191f28;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.route-value.placeholder {
  color: #b0b8c1;
  font-weight: 400;
}

.current-location-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: #e7f1ff;
  color: #3182f6;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.current-location-btn:hover {
  background: #3182f6;
  color: #fff;
}

.route-divider {
  display: flex;
  align-items: center;
  padding: 4px 12px;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: #e5e8eb;
}

.swap-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f2f4f6;
  color: #6b7684;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 8px;
  transition: all 0.2s;
}

.swap-btn:hover:not(:disabled) {
  background: #3182f6;
  color: #fff;
}

.swap-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 선택 모드 안내 */
.selection-guide {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding: 12px 16px;
  background: #e7f1ff;
  border-radius: 12px;
}

.guide-content {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #3182f6;
}

.cancel-btn {
  padding: 6px 12px;
  background: #fff;
  color: #6b7684;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
}

/* 지도 섹션 */
.map-section {
  margin-top: 16px;
}

.map-container {
  position: relative;
  height: 300px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.kakao-map {
  width: 100%;
  height: 100%;
}

.map-controls {
  position: absolute;
  right: 12px;
  top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.map-control-btn {
  width: 40px;
  height: 40px;
  background: #fff;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7684;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.map-control-btn:hover {
  background: #3182f6;
  color: #fff;
}

/* 프리셋 섹션 */
.preset-section {
  margin-top: 24px;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: #191f28;
  margin-bottom: 12px;
}

.preset-list {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 4px;
  -webkit-overflow-scrolling: touch;
}

.preset-list::-webkit-scrollbar {
  display: none;
}

.preset-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  background: #fff;
  border-radius: 16px;
  min-width: 80px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.2s;
}

.preset-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.preset-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.preset-name {
  font-size: 13px;
  font-weight: 600;
  color: #4e5968;
}

/* 경로 정보 섹션 */
.route-info-section {
  margin-top: 24px;
}

.route-info-card {
  display: flex;
  gap: 12px;
}

.route-stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: #3182f6;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #8b95a1;
}

.bottom-spacer {
  height: 80px;
}

/* 하단 이동 버튼 */
.bottom-action {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  padding-bottom: max(16px, env(safe-area-inset-bottom));
  background: linear-gradient(to top, #fff 80%, transparent);
}

.start-navigation-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px;
  background: linear-gradient(135deg, #3182f6 0%, #5BA0F5 100%);
  color: #fff;
  border-radius: 16px;
  font-size: 17px;
  font-weight: 700;
  box-shadow: 0 4px 16px rgba(49, 130, 246, 0.4);
  transition: all 0.2s;
}

.start-navigation-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(49, 130, 246, 0.5);
}

.start-navigation-btn:active {
  transform: translateY(0);
}
</style>
