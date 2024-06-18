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

import com.wizontech.adtcaps.service.PatternService;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;

@Api(tags = { "PATTERN_API 정보를 제공하는 Controller" })
@RestController
@RequestMapping("/rest/1.0/caps")
public class PatternController {

    @Autowired
    PatternService patternService;

    @ApiOperation(value = "배열 조회", notes = "패턴기준정보 데이터를 전체 조회합니다.")
    @GetMapping("/troublePattern")
    public ResponseEntity<Map<String, Object>> getPatternList() {

        return patternService.getPatternList();
    }

    @ApiOperation(value = "등록", notes = "패턴기준정보 데이터를 등록합니다.")
    @PostMapping("/troublePattern")
    public ResponseEntity<Map<String, String>> insertPattern(@RequestBody String bodyData) {

        return patternService.insertPattern(bodyData);
    }

    @ApiOperation(value = "수정", notes = "패턴기준정보 데이터를 수정합니다.")
    @PutMapping("/troublePattern")
    public ResponseEntity<Map<String, String>> updatePattern(@RequestBody String bodyData) {

        return patternService.updatePattern(bodyData);
    }

    @ApiOperation(value = "삭제", notes = "패턴기준정보 데이터를 삭제합니다.")
    @DeleteMapping("/troublePattern")
    public ResponseEntity<Map<String, String>> deletePattern(@RequestBody String bodyData) {

        return patternService.deletePattern(bodyData);
    }
}