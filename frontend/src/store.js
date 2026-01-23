import { reactive } from 'vue';

export const robotState = reactive({
  name: '해피 (GAE-001)',
  status: 'ONLINE', // ONLINE, OFFLINE
  battery: 100,
  location: '서울시 강남구 역삼동',
  logs: [
    { time: '14:30', msg: '집 도착 완료', type: 'info' },
    { time: '14:10', msg: '산책 시작', type: 'info' }
  ],
  
  // 로봇 상태를 업데이트하는 함수
  updateStatus(data) {
    if (data.battery !== undefined) this.battery = data.battery;
    if (data.status !== undefined) this.status = data.status;
  },
  
  // 로그 추가 함수
  addLog(msg, type = 'info') {
    const time = new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
    this.logs.unshift({ time, msg, type });
  }
});