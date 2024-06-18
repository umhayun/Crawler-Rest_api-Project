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

import com.wizontech.adtcaps.service.IndustryService;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;

@Api(tags = { "INDUSTRY_API 정보를 제공하는 Controller" })
@RestController
@RequestMapping("/rest/1.0/caps")
public class IndustryController {

    @Autowired
    IndustryService industryService;

    @ApiOperation(value = "배열 조회", notes = "업종/Gross/GVip 데이터를 전체 조회합니다.")
    @GetMapping("/troubleIndustry")
    public ResponseEntity<Map<String, Object>> getIndustryList() {

        return industryService.getIndustryList();
    }

    @ApiOperation(value = "배열 등록", notes = "업종/Gross/GVip 데이터를 다중 등록합니다.")
    @PostMapping("/troubleIndustry")
    public ResponseEntity<Map<String, String>> insertAllIndustry(@RequestBody String bodyData) {

        return industryService.insertAllIndustry(bodyData);
    }

    @ApiOperation(value = "수정", notes = "업종/Gross/GVip 데이터를 수정합니다.")
    @PutMapping("/troubleIndustry")
    public ResponseEntity<Map<String, String>> updateIndustry(@RequestBody String bodyData) {

        return industryService.updateIndustry(bodyData);
    }

    @ApiOperation(value = "삭제", notes = "업종/Gross/GVip 데이터를 삭제합니다.")
    @DeleteMapping("/troubleIndustry")
    public ResponseEntity<Map<String, String>> deleteIndustry(@RequestBody String bodyData) {

        return industryService.deleteIndustry(bodyData);
    }

}
