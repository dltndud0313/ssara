package com.gae.server.api.auth;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class EmailService {

    private final JavaMailSender mailSender;

    /**
     * 임시 비밀번호 이메일 발송
     * (테스트 모드: 콘솔에 출력)
     */
    public void sendTempPassword(String toEmail, String tempPassword) {
        // TODO: 실제 운영 시 아래 주석 해제하고 콘솔 출력 부분 삭제
        /*
        SimpleMailMessage message = new SimpleMailMessage();
        message.setTo(toEmail);
        message.setSubject("[파트라슈 봇] 임시 비밀번호 안내");
        message.setText(
                "안녕하세요, 파트라슈 봇입니다.\n\n" +
                "요청하신 임시 비밀번호를 안내해 드립니다.\n\n" +
                "━━━━━━━━━━━━━━━━━━━━\n" +
                "임시 비밀번호: " + tempPassword + "\n" +
                "━━━━━━━━━━━━━━━━━━━━\n\n" +
                "로그인 후 반드시 비밀번호를 변경해 주세요.\n\n" +
                "감사합니다."
        );

        try {
            mailSender.send(message);
            log.info("임시 비밀번호 이메일 발송 완료: {}", toEmail);
        } catch (Exception e) {
            log.error("이메일 발송 실패: {}", e.getMessage());
            throw new RuntimeException("이메일 발송에 실패했습니다.");
        }
        */

        // 테스트용: 콘솔에 임시 비밀번호 출력
        log.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        log.info("📧 임시 비밀번호 발송 (테스트 모드)");
        log.info("수신자: {}", toEmail);
        log.info("임시 비밀번호: {}", tempPassword);
        log.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    }
}
