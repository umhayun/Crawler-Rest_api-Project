package com.wizontech.adtcaps.controller;

import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.wizontech.adtcaps.service.ContractService;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;


@Api(tags = { "CONTRACT 정보 제공하는 Controller" })
@RestController
@RequestMapping("/rest/1.0/caps")
public class ContractController {
    @Autowired
    ContractService contractService;


    @ApiOperation(value = "info조회", notes = "계약 정보 데이터를 수정합니다.")
    @PostMapping("/getContractInfo")
    public ResponseEntity<Map<String, String>> getContractInfo(@RequestBody String bodyData) {
        return contractService.getContractInfoList(bodyData);
    }

    @ApiOperation(value = "info수정", notes = "계약 정보 데이터를 수정합니다.")
    @PostMapping("/contractInfo")
    public ResponseEntity<Map<String, String>> updateContractInfo(@RequestBody String bodyData) {
        return contractService.updateContractInfo(bodyData);
    }
}
