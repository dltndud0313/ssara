# SMTP 이메일 발송 구현 가이드

Spring Boot + Gmail SMTP를 이용한 임시 비밀번호 발송 기능 구현 과정

---

## 1. Gmail 앱 비밀번호 발급

Gmail SMTP를 사용하려면 일반 비밀번호가 아닌 **앱 비밀번호**가 필요합니다.

### 발급 순서
1. Google 계정 로그인
2. [Google 계정 관리](https://myaccount.google.com/) 접속
3. **보안** 탭 클릭
4. **2단계 인증** 활성화 (필수)
5. 2단계 인증 설정 완료 후, **앱 비밀번호** 메뉴 진입
6. 앱 선택: `메일`, 기기 선택: `Windows 컴퓨터` (또는 기타)
7. **생성** 클릭 → 16자리 비밀번호 발급 (예: `abcd efgh ijkl mnop`)

> 이 16자리 비밀번호를 application-dev.yml에 입력합니다.

---

## 2. Spring Boot 메일 설정

### 2-1. 의존성 추가 (build.gradle)

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-mail'
}
```

### 2-2. application-dev.yml 설정

```yaml
spring:
  mail:
    host: smtp.gmail.com
    port: 587
    username: your-email@gmail.com      # 본인 Gmail 주소
    password: abcd efgh ijkl mnop       # 앱 비밀번호 (16자리)
    properties:
      mail:
        smtp:
          auth: true
          starttls:
            enable: true
```

**파일 위치:** `backend/src/main/resources/application-dev.yml`

---

## 3. EmailService 구현

### 파일 위치
`backend/src/main/java/com/gae/server/api/auth/EmailService.java`

### 코드

```java
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
     */
    public void sendTempPassword(String toEmail, String tempPassword) {
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
    }
}
```

---

## 4. AuthService에서 호출

### 파일 위치
`backend/src/main/java/com/gae/server/api/auth/AuthService.java`

### 핵심 코드

```java
@Service
@RequiredArgsConstructor
public class AuthService {

    private final EmailService emailService;
    private final MemberRepository memberRepository;
    private final PasswordEncoder passwordEncoder;

    // 임시 비밀번호 발송
    @Transactional
    public void sendTempPassword(SendTempPasswordRequest request) {
        // 1. 이메일로 회원 조회
        Member member = memberRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new RuntimeException("가입되지 않은 이메일입니다."));

        // 2. 임시 비밀번호 생성 (8자리)
        String tempPassword = generateTempPassword();

        // 3. DB에 암호화된 임시 비밀번호 저장
        member.updatePassword(passwordEncoder.encode(tempPassword));

        // 4. 이메일 발송
        emailService.sendTempPassword(member.getEmail(), tempPassword);
    }

    // 임시 비밀번호 생성
    private String generateTempPassword() {
        String chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789";
        SecureRandom random = new SecureRandom();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 8; i++) {
            sb.append(chars.charAt(random.nextInt(chars.length())));
        }
        return sb.toString();
    }
}
```

---

## 5. API Controller

### 파일 위치
`backend/src/main/java/com/gae/server/api/auth/AuthController.java`

### 엔드포인트

```java
@PostMapping("/send-temp-password")
public ResponseEntity<String> sendTempPassword(@Valid @RequestBody SendTempPasswordRequest request) {
    authService.sendTempPassword(request);
    return ResponseEntity.ok("임시 비밀번호가 이메일로 발송되었습니다.");
}
```

**API:** `POST /api/auth/send-temp-password`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

---

## 6. 발생했던 에러 및 해결

### 에러 1: 이메일이 발송되지 않음

**원인:** EmailService에서 실제 발송 코드가 주석 처리되어 있었음 (테스트 모드)

**해결:** 주석 해제
```java
// 변경 전: 콘솔에만 출력
log.info("임시 비밀번호: {}", tempPassword);

// 변경 후: 실제 이메일 발송
mailSender.send(message);
```

### 에러 2: 코드 수정 후에도 이전 코드로 동작

**원인:** 서버 재시작을 하지 않아서 이전 코드로 실행 중이었음

**해결:** 서버 완전 재시작
```bash
# 1. 포트 사용 중인 프로세스 확인
netstat -ano | findstr :8080

# 2. 프로세스 종료 (PID 확인 후)
taskkill //F //PID [PID번호]

# 3. 서버 재시작
./gradlew bootRun
```

### 에러 3: curl에서 한글 깨짐 (JSON parse error)

**원인:** Windows cmd에서 한글 인코딩 문제

**해결:** 테스트 시 영문 사용 또는 Postman 사용

---

## 7. 테스트 방법

### curl로 테스트

```bash
# 1. 회원가입
curl -X POST http://localhost:8080/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@gmail.com", "password":"test1234", "name":"Test", "phoneNumber":"010-1234-5678", "serialNumber":"TEST-001"}'

# 2. 임시 비밀번호 발송
curl -X POST http://localhost:8080/api/auth/send-temp-password \
  -H "Content-Type: application/json" \
  -d '{"email":"test@gmail.com"}'
```

### 프론트엔드에서 테스트

1. 로그인 페이지 접속
2. "비밀번호 찾기" 클릭
3. 이메일 입력 후 "임시 비밀번호 받기" 클릭
4. 이메일 확인 (스팸함도 확인)

---

## 8. 전체 흐름 요약

```
[사용자] 비밀번호 찾기 요청
    ↓
[프론트엔드] POST /api/auth/send-temp-password { email }
    ↓
[AuthController] sendTempPassword() 호출
    ↓
[AuthService]
    1. 이메일로 회원 조회
    2. 임시 비밀번호 생성 (8자리)
    3. DB에 암호화된 비밀번호 저장
    4. EmailService 호출
    ↓
[EmailService]
    1. SimpleMailMessage 생성
    2. JavaMailSender로 발송
    ↓
[Gmail SMTP] → [사용자 메일함]
```

---

## 9. 주의사항

1. **앱 비밀번호는 절대 Git에 커밋하지 않기** → `.gitignore`에 추가하거나 환경변수 사용
2. **운영 환경에서는 환경변수 사용** (`application-prod.yml` 참고)
3. **메일이 스팸함으로 갈 수 있음** → 테스트 시 스팸함도 확인
4. **Gmail 일일 발송 제한**: 무료 계정은 하루 500통 제한 -> 확인하기! 
