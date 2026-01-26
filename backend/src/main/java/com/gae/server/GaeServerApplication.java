package com.gae.server;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

@SpringBootApplication
@EnableJpaAuditing
public class GaeServerApplication {

    public static void main(String[] args) {
        SpringApplication.run(GaeServerApplication.class, args);
    }

}
