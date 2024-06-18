package com.wizontech.adtcaps;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

@ComponentScan
@EnableAutoConfiguration
@SpringBootApplication
public class ADTCollectorApplication {
    public static void main(String[] args) {
        SpringApplication.run(ADTCollectorApplication.class, args);
    }
}
