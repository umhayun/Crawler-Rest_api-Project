package com.wizontech.adtcaps.service;

import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.wizontech.adtcaps.dao.EquipmentDAO;
import com.wizontech.adtcaps.dao.HealthDao;
import com.wizontech.adtcaps.entity.EquipmentData;
import com.wizontech.adtcaps.entity.EquipmentInfoData;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class EquipmentService {

    @Autowired
    private EquipmentDAO equipmentDAO;

    @Autowired
    private HealthDao healthDao;



    HttpStatus status = HttpStatus.INTERNAL_SERVER_ERROR;
    Gson gson = new Gson();

    public ResponseEntity<Map<String, Object>> getEquipmentList() {
        Map<String, Object> resMap = new HashMap<>();
        List<EquipmentData> equipmentList = equipmentDAO.getEquipmentList();

        if (equipmentList.size() > 0) {
            resMap.put("EquipmenTotal", equipmentList);
            status = HttpStatus.OK;
        } else {
            resMap.put("message", "failure");
            status = HttpStatus.BAD_REQUEST;
            log.error("***** equipmentList is null!");
        }

        return new ResponseEntity<>(resMap, status);
    }

    public ResponseEntity<Map<String, String>> insertEquipment(String bodyData) {
        Map<String, String> resMap = new HashMap<>();

        resMap.put("message", "failure");
        status = HttpStatus.BAD_REQUEST;

        try {
            EquipmentData equipmentData = gson.fromJson(bodyData, EquipmentData.class);
            int result = equipmentDAO.insertEquipment(equipmentData);

            if (result == 1) {
                resMap.put("message", "success");
                status = HttpStatus.OK;
                log.info("==> insert success! // NVRSN :: " + equipmentData.getNVRSN());
            } else {

                log.error("==> insert failure! // NVRSN :: " + equipmentData.getNVRSN());
            }
        } catch (Exception e) {
            log.error(e.toString());
            log.error("******* bodyData :: ");
            log.error(bodyData);
        }

        return new ResponseEntity<>(resMap, status);
    }

    public ResponseEntity<Map<String, String>> updateEquipment(String bodyData) {
        Map<String, String> resMap = new HashMap<>();

        resMap.put("message", "failure");
        status = HttpStatus.BAD_REQUEST;

        try {
            EquipmentData equipmentData = gson.fromJson(bodyData, EquipmentData.class);
            int result = equipmentDAO.updateEquipment(equipmentData);

            if (result == 1) {
                resMap.put("message", "success");
                status = HttpStatus.OK;
                log.info("==> update success! // NVRSN :: " + equipmentData.getNVRSN());
            } else {
                log.error("==> update failure! // NVRSN :: " + equipmentData.getNVRSN());
            }
        } catch (Exception e) {
            log.error(e.toString());
            log.error("==> bodyData :: ");
            log.error(bodyData);
        }

        return new ResponseEntity<>(resMap, status);
    }

    public ResponseEntity<Map<String, String>> deleteEquipment(String bodyData) {
        Map<String, String> resMap = new HashMap<>();

        resMap.put("message", "failure");
        status = HttpStatus.BAD_REQUEST;

        try {
            EquipmentData equipmentData = gson.fromJson(bodyData, EquipmentData.class);
            String NVRSN = equipmentData.getNVRSN();
            int result = equipmentDAO.deleteEquipment(NVRSN);

            if (result == 1) {
                resMap.put("message", "success");
                status = HttpStatus.OK;
                log.info("==> delete success! // NVRSN :: " + NVRSN);
            } else {
                log.error("==> delete failure! // NVRSN :: " + NVRSN);
            }
        } catch (Exception e) {
            log.error(e.toString());
            log.error("==> bodyData :: ");
            log.error(bodyData);
        }

        return new ResponseEntity<Map<String, String>>(resMap, status);
    }

    //Equipment Info
    //select
    public ResponseEntity<Map<String, String>> getEquipmentInfoList(String bodyData) {
        log.info("[POST] EQUIPMENTINFO SELECT ACCESS ");
        Map<String, String> resMap = new LinkedHashMap<>();
        status = HttpStatus.BAD_REQUEST;
        resMap.put("message", "failure");
        try {      
                EquipmentInfoData equipmentInfoData = gson.fromJson(bodyData, EquipmentInfoData.class);
                int num=equipmentInfoData.getNum();
                EquipmentInfoData result=equipmentDAO.getEquipmentInfoNumlist(num);

                if(num!=0){
                    if (result!=null && num==result.getNum()){     
                        resMap.put("message","success");
                        resMap.put("num",String.valueOf(result.getNum()));
                        resMap.put("sn",result.getSn());
                        resMap.put("mac", result.getMac());
                        resMap.put("contract_no", result.getContract_no());  
                        resMap.put("account_no",result.getAccount_no());                       
                        status=HttpStatus.OK;
                        log.info("==> SELECT SUCCESS! // SN :: " + result.getSn());
                    }
                    else{
                        status=HttpStatus.OK;   
                        log.info("==> SELECT SUCCESS! // SN :: NO DATA");                     
                    }
                }
                else{
                    resMap.put("message", "failure");
                    log.error("==> SELECT FAILURE! // SN :: " + result.getSn());
                }

        } catch (Exception e) {
            log.error(e.toString());
            log.error("==> bodyData :: ");
            log.error(bodyData);
        }

        return new ResponseEntity<>(resMap, status);
        }
    //insert
    public ResponseEntity<Map<String, String>> insertEquipmentInfo(String bodyData) {

        log.info("[PUT] EQUIPMENTINFO INSERT ACCESS ");
        Map<String, String> resMap = new HashMap<>();

        resMap.put("message", "failure");
        status = HttpStatus.BAD_REQUEST;
        
        JsonObject equipments = gson.fromJson(bodyData,JsonObject.class);
        JsonArray equipArr=equipments.get("equipment_list").getAsJsonArray();   
    
        for (JsonElement equipElement : equipArr) { 
            try {
                
                EquipmentInfoData equipmentInfoData = gson.fromJson(equipElement, EquipmentInfoData.class);  
                String sn= equipmentInfoData.getSn();
                int num=equipmentInfoData.getNum();
                EquipmentInfoData selectData=equipmentDAO.getEquipmentInfolist(sn);
                EquipmentInfoData numData=equipmentDAO.getEquipmentInfoNumlist(num);
                int result=0;
                if (selectData==null && numData==null){
                    result=equipmentDAO.insertEquipmentInfo(equipmentInfoData);
                    if (result>0){
                        resMap.put("message", "success");
                        status=HttpStatus.OK;
                    }
                    else{
                        log.error("==> INSERT FAILURE! // SN :: " + equipmentInfoData.getSn());
                    } 
                }
                else  {
                    if (selectData!=null){
                        if(selectData.getNum()<equipmentInfoData.getNum() && sn.equals(selectData.getSn())){
                            status=HttpStatus.OK;
                            resMap.put("message", "success");
                        }
                        else if(selectData.getNum()==equipmentInfoData.getNum() && sn.equals(selectData.getSn())){

                            log.info("==> EXISTS DATA! // SN :: " + equipmentInfoData.getSn());
                        }
                    }
                    if(numData!=null){
                        if(num==numData.getNum() && !sn.equals(numData.getSn())) {
                            log.error("==> INSERT FAILURE! // SN :: " + equipmentInfoData.getSn());
                        }
                    }             
                    else{
                        log.error("==> INSERT FAILURE! // SN :: " + equipmentInfoData.getSn());
                    }
                }
                

            } catch (Exception e) {
                log.error(e.toString());
                log.error("==> bodyData :: ");
                log.error(bodyData);
            }
        } 
        log.info("EQUIPMENTINFO INSERT FINISH : " + equipArr.size());
        healthDao.selectEquipmentInfoList();
        return new ResponseEntity<Map<String, String>>(resMap, status); 
    }


    //update
    public ResponseEntity<Map<String, String>> updateEquipmentInfo(String bodyData) {
        log.info("[POST] EQUIPMENTINFO UPDATE ACCESS ");
        Map<String, String> resMap = new HashMap<>();
        int result=0;
        resMap.put("message", "failure");
        status = HttpStatus.BAD_REQUEST;
        JsonObject equipments = gson.fromJson(bodyData,JsonObject.class);
        JsonArray equipArr=equipments.get("equipment_list").getAsJsonArray();   
        for (JsonElement equipElement : equipArr) { 
            try {
                EquipmentInfoData equipmentInfoData = gson.fromJson(equipElement, EquipmentInfoData.class);
                String sn =equipmentInfoData.getSn();
                int num = equipmentInfoData.getNum();
                EquipmentInfoData selectData= equipmentDAO.getEquipmentInfolist(sn);

                EquipmentInfoData numData=equipmentDAO.getEquipmentInfoNumlist(num);

                if(selectData!=null&&(numData==null|| numData!=null)){
                    if (selectData.getNum()>=equipmentInfoData.getNum()){
                        result = equipmentDAO.updateEquipmentInfo(equipmentInfoData);
                        if (result > 0) {
                            resMap.put("message", "success");
                            status = HttpStatus.OK;
                        } else {
                            log.error("==> UPDATE FAILURE! // SN :: " + equipmentInfoData.getSn());
                        } 
                    }else if(selectData.getNum()<equipmentInfoData.getNum()){
                        status = HttpStatus.OK;
                        resMap.put("message", "success");
                        log.info("==> EXISTS NUMBER! // SN :: " + equipmentInfoData.getNum());
                    }                                                       
                }         
                else{
                    log.error("==> NO DATA! // SN :: " + equipmentInfoData.getSn());
                }
                
                
            } catch (Exception e) {
                log.error(e.toString());
                log.error("==> bodyData :: ");
                log.error(bodyData);
            }
        }
        log.info("EQUIPMENTINFO UPDATE SUCCESS : "+result+"/"+equipArr.size());
        healthDao.selectEquipmentInfoList();
        return new ResponseEntity<>(resMap, status);
    }

    //delete
    public ResponseEntity<Map<String, String>> deleteEquipmentInfo(String bodyData) {
        log.info("[DELETE] EQUIPMENTINFO DELETE ACCESS ");
        Map<String, String> resMap = new HashMap<>();

        resMap.put("message", "failure");
        status = HttpStatus.BAD_REQUEST;
        JsonObject equipments = gson.fromJson(bodyData,JsonObject.class);
        JsonArray equipArr=equipments.get("equipment_list").getAsJsonArray();   
        for (JsonElement equipElement : equipArr) { 
            try {
                EquipmentInfoData equipmentInfoData = gson.fromJson(equipElement, EquipmentInfoData.class);
                int num = equipmentInfoData.getNum();
                int result = equipmentDAO.deleteEquipmentInfo(num);
                if (result >0) {
                    resMap.put("message", "success");
                    status = HttpStatus.OK;
                    
                } else {
                    log.error("==> EQUIPMENTINFO DELETE FAILURE! // NUM :: " + num);
                }
            } catch (Exception e) {
                log.error(e.toString());
                log.error("==> bodyData :: ");
                log.error(bodyData);
            }
        }
        log.info("EQUIPMENTINFO DELETE FINISH : " + equipArr.size());
        healthDao.selectEquipmentInfoList();
        
        return new ResponseEntity<Map<String, String>>(resMap, status);    
    }



}