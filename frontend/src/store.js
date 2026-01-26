import { reactive } from 'vue';

export const robotState = reactive({
  name: '',
  status: 'OFFLINE', // ONLINE, OFFLINE
  battery: 0,
  location: '',
  logs: [],
  
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