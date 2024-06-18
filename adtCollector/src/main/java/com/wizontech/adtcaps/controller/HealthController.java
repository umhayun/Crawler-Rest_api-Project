package com.wizontech.adtcaps.controller;

import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.wizontech.adtcaps.service.HealthService;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;


@Api(tags = { "장애이력 정보를 제공하는 Controller" })
@RestController
@RequestMapping("/rest/1.0/caps")
public class HealthController {

    @Autowired
    HealthService healthService;
    
    @ApiOperation(value = "장애발생 리스트 카운트 요청", notes = "장애 발생 리스트 카운트하기")
    @PostMapping("/healthCount")
    public ResponseEntity<Map<String, Object>> getHealthCount(@RequestBody String bodyData) {

        return healthService.getHealthCount(bodyData);
    }

    @ApiOperation(value = "장애 이력 조회", notes = "장애 발생 리스트 출력")
    @PostMapping("/healthInfo")
    public ResponseEntity<Map<String, Object>> getHeathInfo(@RequestBody String bodyData) {
        
        return healthService.getHealthInfo(bodyData);
    }

}
