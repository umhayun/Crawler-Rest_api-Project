package com.wizontech.adtcaps.controller;

import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.wizontech.adtcaps.service.ConditionService;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;

@Api(tags = { "CONDITION_API 정보를 제공하는 Controller" })
@RestController
@RequestMapping("/rest/1.0/caps")
public class ConditionController {

    @Autowired
    ConditionService conditionService;

    @ApiOperation(value = "배열 조회", notes = "장애기준정보 데이터를 전체 조회합니다.")
    @GetMapping("/troubleCondition")
    public ResponseEntity<Map<String, Object>> getConditionList() {

        return conditionService.getConditionList();
    }

    @ApiOperation(value = "등록", notes = "장애기준정보 데이터를 등록합니다.")
    @PostMapping("/troubleCondition")
    public ResponseEntity<Map<String, String>> insertCondition(@RequestBody String bodyData) {

        return conditionService.insertCondition(bodyData);
    }

    @ApiOperation(value = "수정", notes = "장애기준정보 데이터를 수정합니다.")
    @PutMapping("/troubleCondition")
    public ResponseEntity<Map<String, String>> updateCondition(@RequestBody String bodyData) {

        return conditionService.updateCondition(bodyData);
    }

    @ApiOperation(value = "삭제", notes = "장애기준정보 데이터를 삭제합니다.")
    @DeleteMapping("/troubleCondition")
    public ResponseEntity<Map<String, String>> deleteCondition(@RequestBody String bodyData) {

        return conditionService.deleteCondition(bodyData);
    }
}