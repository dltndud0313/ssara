import { defineStore } from 'pinia'
import { ref } from 'vue'
import { Client } from '@stomp/stompjs'
import { robotApi } from '@/api'

export const useRobotStore = defineStore('robot', () => {
  // ==================== State ====================
  const robotStatus = ref({
    battery: 0,
    state: 'UNKNOWN',
    isOnline: false
  })

  const robotPose = ref({
    x: 0,
    y: 0
  })

  // 일일 요약 (산책시간, 이상감지 등)
  const dailySummary = ref({
    walkTime: 0,
    alerts: 0,
    distance: 0,
    totalEvents: 0
  })

  // 최근 활동 로그
  const activityLogs = ref([])

  const isConnected = ref(false)
  let stompClient = null

  // ==================== Actions ====================

  /**
   * WebSocket 연결 및 토픽 구독
   */
  function connectWebSocket() {
    // 이미 연결되어 있으면 무시
    if (stompClient && isConnected.value) {
      console.log('이미 WebSocket에 연결되어 있습니다.')
      return
    }

    stompClient = new Client({
      brokerURL: 'ws://localhost:8080/ws/websocket',
      reconnectDelay: 5000,
      heartbeatIncoming: 4000,
      heartbeatOutgoing: 4000,
      debug: (str) => {
        console.log('[STOMP]', str)
      },

      onConnect: () => {
        console.log('WebSocket 연결됨!')
        isConnected.value = true

        // robot/status 구독
        stompClient.subscribe('/topic/robot/status', (message) => {
          try {
            const data = JSON.parse(message.body)
            robotStatus.value = {
              battery: data.battery ?? 0,
              state: data.state ?? 'UNKNOWN',
              isOnline: data.isOnline ?? false
            }
            console.log('Status 업데이트:', robotStatus.value)
          } catch (e) {
            console.error('Status 파싱 오류:', e)
          }
        })

        // robot/pose 구독
        stompClient.subscribe('/topic/robot/pose', (message) => {
          try {
            const data = JSON.parse(message.body)
            robotPose.value = {
              x: data.x ?? 0,
              y: data.y ?? 0
            }
            console.log('Pose 업데이트:', robotPose.value)
          } catch (e) {
            console.error('Pose 파싱 오류:', e)
          }
        })

        // robot/summary 구독 (산책시간, 이상감지 등)
        stompClient.subscribe('/topic/robot/summary', (message) => {
          try {
            const data = JSON.parse(message.body)
            dailySummary.value = {
              walkTime: data.walkTime ?? 0,
              alerts: data.alerts ?? 0,
              distance: data.distance ?? 0,
              totalEvents: data.totalEvents ?? 0
            }
            console.log('Summary 업데이트:', dailySummary.value)
          } catch (e) {
            console.error('Summary 파싱 오류:', e)
          }
        })

        // robot/activity 구독 (이상 감지 이벤트)
        stompClient.subscribe('/topic/robot/activity', (message) => {
          try {
            const data = JSON.parse(message.body)
            const log = {
              type: data.severity === 'HIGH' ? 'warning' : 'info',
              msg: data.message ?? '알 수 없는 이벤트',
              time: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
            }
            activityLogs.value.unshift(log)
            // 최대 10개 유지
            if (activityLogs.value.length > 10) {
              activityLogs.value.pop()
            }
            console.log('Activity 추가:', log)
          } catch (e) {
            console.error('Activity 파싱 오류:', e)
          }
        })
      },

      onDisconnect: () => {
        console.log('WebSocket 연결 끊김')
        isConnected.value = false
      },

      onStompError: (frame) => {
        console.error('STOMP 오류:', frame.headers['message'])
        isConnected.value = false
      },

      onWebSocketError: (event) => {
        console.error('WebSocket 오류:', event)
        isConnected.value = false
      }
    })

    stompClient.activate()
  }

  /**
   * WebSocket 연결 해제
   */
  function disconnectWebSocket() {
    if (stompClient) {
      stompClient.deactivate()
      stompClient = null
      isConnected.value = false
    }
  }

  /**
   * 집으로 복귀 명령
   */
  async function sendHomeCommand() {
    try {
      const response = await robotApi.sendHome()
      console.log('Home 명령 전송:', response.data)
      return response.data
    } catch (error) {
      console.error('Home 명령 실패:', error)
      throw error
    }
  }

  /**
   * 정지 명령 (Rosbridge Protocol)
   */
  async function sendStopCommand() {
    try {
      const response = await robotApi.sendStop()
      console.log('Stop 명령 전송 (Rosbridge):', response.data)
      return response.data
    } catch (error) {
      console.error('Stop 명령 실패:', error)
      throw error
    }
  }

  /**
   * 속도 제어 명령 (Rosbridge Protocol)
   * @param {number} linearX - 전진(+)/후진(-) 속도 (-1.0 ~ 1.0)
   * @param {number} angularZ - 좌회전(+)/우회전(-) 각속도 (-1.0 ~ 1.0)
   */
  async function sendVelocityCommand(linearX, angularZ) {
    try {
      const response = await robotApi.sendVelocity(linearX, angularZ)
      console.log('Velocity 명령 전송 (Rosbridge):', response.data)
      return response.data
    } catch (error) {
      console.error('Velocity 명령 실패:', error)
      throw error
    }
  }

  /**
   * 좌표 이동 명령
   */
  async function sendNavCommand(x, y) {
    try {
      const response = await robotApi.sendNav(x, y)
      console.log('Nav 명령 전송:', response.data)
      return response.data
    } catch (error) {
      console.error('Nav 명령 실패:', error)
      throw error
    }
  }

  return {
    // State
    robotStatus,
    robotPose,
    dailySummary,
    activityLogs,
    isConnected,
    // Actions
    connectWebSocket,
    disconnectWebSocket,
    sendHomeCommand,
    sendStopCommand,
    sendVelocityCommand,
    sendNavCommand
  }
})
