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

import com.wizontech.adtcaps.service.EquipmentService;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;


@Api(tags = { "EQUIPMENT_API 정보를 제공및 저장하는 Controller" })
@RestController
@RequestMapping("/rest/1.0/caps")
public class EquipmentController {

    @Autowired
    EquipmentService equipmentService;

    @ApiOperation(value = "배열 조회", notes = "녹화기장애리스트 데이터를 전체 조회합니다.")
    @GetMapping("/troubleEquipment")
    public ResponseEntity<Map<String, Object>> getEquipmentList() {

        return equipmentService.getEquipmentList();
    }

    @ApiOperation(value = "등록", notes = "녹화기장애리스트 데이터를 등록합니다.")
    @PostMapping("/troubleEquipment")
    public ResponseEntity<Map<String, String>> insertEquipment(@RequestBody String bodyData) {

        return equipmentService.insertEquipment(bodyData);
    }

    @ApiOperation(value = "수정", notes = "녹화기장애리스트 데이터를 수정합니다.")
    @PutMapping("/troubleEquipment")
    public ResponseEntity<Map<String, String>> updateEquipment(@RequestBody String bodyData) {

        return equipmentService.updateEquipment(bodyData);
    }

    @ApiOperation(value = "삭제", notes = "녹화기장애리스트 데이터를 삭제합니다.")
    @DeleteMapping("/troubleEquipment")
    public ResponseEntity<Map<String, String>> deleteEquipment(@RequestBody String bodyData) {

        return equipmentService.deleteEquipment(bodyData);
    }

    //Equipment Info 
    @ApiOperation(value = "info조회", notes = "장비 정보 데이터를 저장합니다.")
    @PostMapping("/getEquipmentInfo")
    public ResponseEntity<Map<String, String>> selectEquipmentInfo(@RequestBody String bodyData) {

        return equipmentService.getEquipmentInfoList(bodyData);
    }

    @ApiOperation(value = "info저장", notes = "장비 정보 데이터를 저장합니다.")
    @PutMapping("/equipmentInfo") 
    public ResponseEntity<Map<String, String>> insertEquipmentInfo(@RequestBody String bodyData) {

        return equipmentService.insertEquipmentInfo(bodyData);
    }

    @ApiOperation(value = "info수정", notes = "장비 정보 데이터를 수정합니다.")
    @PostMapping("/equipmentInfo")
    public ResponseEntity<Map<String, String>> updateEquipmentInfo(@RequestBody String bodyData) {

        return equipmentService.updateEquipmentInfo(bodyData);
    }

    @ApiOperation(value = "info삭제", notes = "장비 데이터를 정보 삭제합니다.")
    @DeleteMapping("/equipmentInfo")
    public ResponseEntity<Map<String, String>> deleteEquipmentInfo(@RequestBody String bodyData) {

        return equipmentService.deleteEquipmentInfo(bodyData);
    } 

}                       