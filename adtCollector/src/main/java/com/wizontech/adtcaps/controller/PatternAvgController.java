package com.wizontech.adtcaps.controller;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.wizontech.adtcaps.service.PatternAvgServise;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiImplicitParam;
import io.swagger.annotations.ApiImplicitParams;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Api(tags = { "PATTERN_AVG_API 정보를 제공하는 Controller" })
@CrossOrigin(origins = "*")
@RestController
@RequestMapping("/rest/1.0/caps")
public class PatternAvgController {

    @Autowired
    PatternAvgServise patternAvgServise;

    @ApiImplicitParams({
            @ApiImplicitParam(name = "Type", value = "type", example = "N", required = false, dataType = "string", paramType = "query"),
            @ApiImplicitParam(name = "Scope", value = "scope", example = "I", required = false, dataType = "string", paramType = "query"),
            @ApiImplicitParam(name = "IndustryCode", value = "업종코드", example = "1234", required = false, dataType = "string", paramType = "query"),
            @ApiImplicitParam(name = "NVRSN", value = "시리얼", example = "90DA6A06B79E", required = false, dataType = "string", paramType = "query")
    })
    @GetMapping("/troublePatternAvg")
    public ResponseEntity<Map<String, Object>> patternAvg(
            @RequestParam(value = "Type", required = true) String type,
            @RequestParam(value = "Scope", required = true) String scope,
            @RequestParam(value = "IndustryCode", required = false) String industryCode,
            @RequestParam(value = "NVRSN", required = false) String nvrsn) {

        log.info("-----------search-----------");
        HttpStatus status = HttpStatus.BAD_REQUEST;
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("message", "failure");

        // String testMac = "90DA6A06B79E"; // 테스트로 임의 지정

        // 네트워크 평균값
        if (type.equals("N") && scope.equals("I")) {
            return patternAvgServise.patternAvg("N", "industry_code", industryCode);

        } else if (type.equals("N") && scope.equals("M")) {
            return patternAvgServise.patternAvg("N", "ddns_mac", nvrsn);

            // 채널로스 평균값
        } else if (type.equals("L")) {
            return patternAvgServise.patternAvg("L", "ddns_mac", nvrsn);
        }

        return new ResponseEntity<>(resultMap, status);
    }
}