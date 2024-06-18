package com.wizontech.adtcaps.controller;

import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.wizontech.adtcaps.service.ArgosService;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;

@Api(tags = { "CONTRACT 정보 제공하는 Controller" })
@RestController
@RequestMapping("/rest/1.0/caps")
public class ArgosController {
    @Autowired
    ArgosService argosService;

    @ApiOperation(value = "argos 전송 여부 수정", notes = "전송 여부 판단 데이터를 수정합니다.")
    @PostMapping("/argosSendStatus")
    public ResponseEntity<Map<String, String>> updateArgosSendStatus(@RequestBody String bodyData) {
        
        return argosService.updateArgosSendStatus(bodyData);
    }
    @ApiOperation(value = "argos 전송 설정값 조회 요청", notes = "전송여부 판단 데이터를 조회합니다")
    @GetMapping("/argosSendStatus")
    public ResponseEntity<Map<String, String>> getArgosSendStatus() {
        
        return argosService.getArgosSendStatus();
    }
}
