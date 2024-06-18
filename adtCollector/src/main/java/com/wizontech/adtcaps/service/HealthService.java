package com.wizontech.adtcaps.service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import com.google.gson.Gson;
import com.wizontech.adtcaps.dao.HealthDao;
import com.wizontech.adtcaps.entity.HealthData;
import com.wizontech.adtcaps.entity.HealthInfoData;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class HealthService {
    HttpStatus status = HttpStatus.INTERNAL_SERVER_ERROR;
    Gson gson = new Gson();

    @Autowired
    HealthDao healthDao;

    public ResponseEntity<Map<String, Object>> getHealthCount(String bodyData) {
        Map<String, Object> resMap = new HashMap<>();
        log.info("[POST] SELECT HEALTHCOUNT ACCESS");
        status = HttpStatus.BAD_REQUEST;
        log.info(bodyData);
        try {
            HealthData healthData = gson.fromJson(bodyData, HealthData.class);
            List<Map<String, String>> results = healthDao.countHealth(healthData);
            resMap.put("Total_Count", results.size());
            status = HttpStatus.OK;
            log.info("SELECT HEALTHCOUNT SUCCESS");
        } catch (Exception e) {
            log.error(e.toString());
            log.error("==> bodyData :: ");
            log.error(bodyData);
        }

        return new ResponseEntity<>(resMap, status);
    }

    public ResponseEntity<Map<String, Object>> getHealthInfo(String bodyData) {
        Map<String, Object> resMap = new LinkedHashMap<>();
        log.info("[POST] SELECT HEALTHINFO ACCESS");
        status = HttpStatus.BAD_REQUEST;
        try {
            HealthInfoData healthInfoData = gson.fromJson(bodyData, HealthInfoData.class);
            resMap.put("Total_Count", healthInfoData.getTotal_Count());
            resMap.put("List_Start_Num", healthInfoData.getList_Start_Num());
            resMap.put("List_End_Num", healthInfoData.getList_End_Num());
            int startnum = healthInfoData.getList_Start_Num() - 1;
            int endnum = healthInfoData.getList_End_Num() - startnum;
            healthInfoData.setList_Start_Num(startnum);
            healthInfoData.setList_End_Num(endnum);
            List<LinkedHashMap<String, Object>> lists = new ArrayList<>();
            List<LinkedHashMap<String, Object>> results = healthDao.getHealthInfo(healthInfoData);
            LinkedHashMap<String, Object> list = new LinkedHashMap<>();
            if (results.size() > 0) {
                for (LinkedHashMap<String, Object> result : results) {
                    list = new LinkedHashMap<>();
                    list.put("ROWNUM", result.get("ROWNUM"));
                    list.put("HARTL_NVRSN", result.get("sn"));
                    list.put("HARTL_Model", result.get("modelNm"));
                    list.put("HARTL_Firm", result.get("firm"));
                    list.put("HARTL_ContractNo", result.get("contractNo"));
                    list.put("HARTL_Accountno", result.get("accountNo"));
                    list.put("HARTL_Signal_Type", result.get("signalType"));
                    list.put("HARTL_Equipment_Type", result.get("equipmentType"));
                    list.put("HARTL_Fault_Type", result.get("faultType"));
                    list.put("HARTL_Fault_Code", result.get("faultCode"));
                    list.put("HARTL_Issuse_Date", result.get("issue_date"));
                    list.put("HARTL_Issuse_Time", result.get("issue_time"));
                    list.put("HARTL_Update_Date", result.get("update_date"));
                    list.put("HARTL_Update_time", result.get("update_time"));
                    lists.add(list);
                }
                log.info("SELECT HEALTHINFO >SUCCESS<");
            } else {
                log.info("SELECT HEALTHINFO >NO DATA<");
            }
            resMap.put("List", lists);
            status = HttpStatus.OK;

        } catch (Exception e) {
            log.error(e.toString());
            log.error("==> bodyData :: ");
            log.error(bodyData);
        }

        return new ResponseEntity<>(resMap, status);
    }

}
