package com.gae.server.api.member.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class MemberUpdateRequest {
    private String name;
    private String phoneNumber;
    private String password;
}