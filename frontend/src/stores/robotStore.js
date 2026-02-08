import { defineStore } from 'pinia'
import { ref } from 'vue'
import { Client } from '@stomp/stompjs'
import mqtt from 'mqtt'
import { robotApi } from '@/api'

export const useRobotStore = defineStore('robot', () => {
  // ==================== State ====================
  const robotStatus = ref({
    battery: 100,
    state: 'UNKNOWN',
    isOnline: false
  })

  const robotPose = ref({
    x: 0,
    y: 0,
    theta: 0
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

  // ==================== VSLAM → GPS 변환 ====================
  const VSLAM_ORIGIN_LAT = 35.20527
  const VSLAM_ORIGIN_LNG = 126.8117
  const VSLAM_HEADING = 0
  const METERS_PER_LAT = 0.000009
  const METERS_PER_LNG = 0.000011

  function vslamToGps(x, y) {
    const headingRad = (VSLAM_HEADING * Math.PI) / 180
    const cosH = Math.cos(headingRad)
    const sinH = Math.sin(headingRad)
    const rotatedX = x * cosH - y * sinH
    const rotatedY = x * sinH + y * cosH
    return {
      lat: VSLAM_ORIGIN_LAT + rotatedY * METERS_PER_LAT,
      lng: VSLAM_ORIGIN_LNG + rotatedX * METERS_PER_LNG
    }
  }

  function getGpsCoord() {
    return vslamToGps(robotPose.value.x || 0, robotPose.value.y || 0)
  }

  const isConnected = ref(false)
  const vslamConnected = ref(false)
  const mqttPoseConnected = ref(false)
  let stompClient = null
  let mqttPoseClient = null
  let vslamTimeout = null

  // ==================== Actions ====================

  /**
   * WebSocket 연결 및 토픽 구독
   * robot/pose 데이터는 MQTT → 백엔드 → WebSocket 경로로 수신
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

        // robot/pose 구독 (MQTT → 백엔드 → WebSocket)
        stompClient.subscribe('/topic/robot/pose', (message) => {
          try {
            const data = JSON.parse(message.body)
            robotPose.value = {
              x: data.x ?? 0,
              y: data.y ?? 0,
              theta: data.theta ?? 0
            }
            if (data.state) {
              robotStatus.value.state = data.state
              robotStatus.value.isOnline = data.state === 'active'
            }
            // pose 데이터가 들어오면 VSLAM 연결 상태 활성화
            vslamConnected.value = true
            resetVslamTimeout()
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
        vslamConnected.value = false
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

    // MQTT Pose도 함께 연결
    connectMqttPose()
  }

  /**
   * VSLAM 연결 상태 타임아웃 (5초간 pose 데이터 없으면 끊김 판정)
   */
  function resetVslamTimeout() {
    if (vslamTimeout) clearTimeout(vslamTimeout)
    vslamTimeout = setTimeout(() => {
      vslamConnected.value = false
    }, 5000)
  }

  // ==================== MQTT Pose 직접 연결 (로봇 → 웹) ====================

  /**
   * MQTT로 로봇 pose 데이터를 직접 수신
   * ws://${import.meta.env.VITE_MQTT_BROKER_IP}:9001, topic: robot/pose
   */
  let mqttPoseRetried = false

  function connectMqttPose() {
    if (mqttPoseClient) return
    mqttPoseRetried = false
    tryMqttPoseConnect('/mqtt')
  }

  function tryMqttPoseConnect(wsPath) {
    if (mqttPoseClient) {
      mqttPoseClient.end(true)
      mqttPoseClient = null
    }

    console.log(`[MQTT Pose] 연결 시도: ws://${import.meta.env.VITE_MQTT_BROKER_IP}:9001 (path: ${wsPath})`)

    mqttPoseClient = mqtt.connect(`ws://${import.meta.env.VITE_MQTT_BROKER_IP}:9001`, {
      reconnectPeriod: 3000,
      connectTimeout: 5000,
      path: wsPath
    })

    // 5초 안에 connect 안 되면 다른 path로 재시도
    const fallbackTimer = setTimeout(() => {
      if (!mqttPoseConnected.value && !mqttPoseRetried) {
        mqttPoseRetried = true
        const altPath = wsPath === '/mqtt' ? '/' : '/mqtt'
        console.log(`[MQTT Pose] path=${wsPath} 실패, path=${altPath}로 재시도`)
        tryMqttPoseConnect(altPath)
      }
    }, 5000)

    mqttPoseClient.on('connect', () => {
      clearTimeout(fallbackTimer)
      console.log(`[MQTT Pose] 연결 성공! (path: ${wsPath})`)
      mqttPoseConnected.value = true
      mqttPoseClient.subscribe('robot/pose', (err) => {
        if (err) console.error('[MQTT Pose] robot/pose 구독 실패:', err)
        else console.log('[MQTT Pose] robot/pose 구독 완료. 데이터 대기 중...')
      })
    })

    mqttPoseClient.on('message', (topic, message) => {
      if (topic === 'robot/pose') {
        try {
          const raw = message.toString()
          const data = JSON.parse(raw)
          robotPose.value = {
            x: data.x ?? 0,
            y: data.y ?? 0,
            theta: data.theta ?? robotPose.value.theta
          }
          if (data.state) {
            robotStatus.value.state = data.state
            robotStatus.value.isOnline = data.state === 'active'
          }
          vslamConnected.value = true
          resetVslamTimeout()

          const now = new Date()
          const ts = `${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}:${now.getSeconds().toString().padStart(2,'0')}.${now.getMilliseconds().toString().padStart(3,'0')}`
          console.log(`[VSLAM ${ts}] x=${data.x}, y=${data.y}, state=${data.state || '-'}  raw=${raw}`)
        } catch (e) {
          console.error('[MQTT Pose] 파싱 오류:', e, 'raw:', message.toString())
        }
      }
    })

    mqttPoseClient.on('error', (err) => {
      console.error('[MQTT Pose] 오류:', err)
      mqttPoseConnected.value = false
    })

    mqttPoseClient.on('reconnect', () => {
      console.log('[MQTT Pose] 재연결 시도...')
    })

    mqttPoseClient.on('close', () => {
      console.log('[MQTT Pose] 연결 끊김')
      mqttPoseConnected.value = false
    })
  }

  function disconnectMqttPose() {
    if (mqttPoseClient) {
      mqttPoseClient.end()
      mqttPoseClient = null
      mqttPoseConnected.value = false
    }
  }

  /**
   * WebSocket 연결 해제
   */
  function disconnectWebSocket() {
    if (stompClient) {
      stompClient.deactivate()
      stompClient = null
      isConnected.value = false
      vslamConnected.value = false
    }
    disconnectMqttPose()
    if (vslamTimeout) {
      clearTimeout(vslamTimeout)
      vslamTimeout = null
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
    vslamConnected,
    mqttPoseConnected,
    // Actions
    connectWebSocket,
    disconnectWebSocket,
    connectMqttPose,
    disconnectMqttPose,
    sendHomeCommand,
    sendStopCommand,
    sendVelocityCommand,
    sendNavCommand,
    getGpsCoord
  }
})
