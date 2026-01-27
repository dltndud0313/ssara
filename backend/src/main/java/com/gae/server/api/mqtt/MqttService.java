package com.gae.server.api.mqtt;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gae.server.api.robot.dto.ros.RosMessage;
import com.gae.server.api.robot.dto.ros.Twist;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.integration.annotation.ServiceActivator;
import org.springframework.messaging.Message;
import org.springframework.messaging.MessageHeaders;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class MqttService {

    private static final String TOPIC_HEADER = "mqtt_receivedTopic";
    private static final String TOPIC_CMD_VEL = "robot/cmd/vel";

    private final SimpMessagingTemplate messagingTemplate;
    private final MqttGateway mqttGateway;
    private final ObjectMapper objectMapper;

    @ServiceActivator(inputChannel = "mqttInputChannel")
    public void handleMessage(Message<?> message) {
        MessageHeaders headers = message.getHeaders();
        String topic = (String) headers.get(TOPIC_HEADER);
        String payload = message.getPayload().toString();

        log.info("MQTT [{}] -> {}", topic, payload);

        // MQTT 토픽을 WebSocket 토픽으로 변환하여 브로드캐스트
        switch (topic) {
            case "robot/status" -> {
                messagingTemplate.convertAndSend("/topic/robot/status", payload);
            }
            case "robot/pose" -> {
                messagingTemplate.convertAndSend("/topic/robot/pose", payload);
            }
            case "robot/map" -> {
                messagingTemplate.convertAndSend("/topic/robot/map", payload);
            }
            default -> log.warn("Unknown MQTT topic: {}", topic);
        }
    }

    /**
     * Rosbridge Protocol 형식으로 로봇 속도 명령 전송
     * @param linearX 전진(+)/후진(-) 속도
     * @param angularZ 좌회전(+)/우회전(-) 각속도
     */
    public void sendVelocity(double linearX, double angularZ) {
        Twist twist = Twist.of(linearX, angularZ);
        RosMessage<Twist> rosMessage = RosMessage.cmdVel(twist);

        try {
            String payload = objectMapper.writeValueAsString(rosMessage);
            mqttGateway.sendToMqtt(payload, TOPIC_CMD_VEL);
            log.info("Velocity command sent: [{}] -> {}", TOPIC_CMD_VEL, payload);
        } catch (JsonProcessingException e) {
            log.error("Failed to serialize ROS message", e);
            throw new RuntimeException("Failed to send velocity command", e);
        }
    }

    /**
     * 로봇 정지 명령 전송
     */
    public void sendStop() {
        sendVelocity(0.0, 0.0);
    }
}
