package com.wizontech.adtcaps.service;

import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.wizontech.adtcaps.dao.ContractDAO;
import com.wizontech.adtcaps.dao.HealthDao;
import com.wizontech.adtcaps.entity.ContractInfoData;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class ContractService {
    @Autowired
    ContractDAO contractDAO;

    @Autowired
    HealthDao healthDao;
    


    HttpStatus status = HttpStatus.INTERNAL_SERVER_ERROR;
    Gson gson = new Gson();
    public ResponseEntity<Map<String, String>> getContractInfoList(String bodyData){
        log.info("[POST] CONTRACTINFO SELECT ACCESS ");
        Map<String, String> resMap = new LinkedHashMap<>();
        status=HttpStatus.BAD_REQUEST;
        resMap.put("message", "failure");
        try {
            ContractInfoData contractInfoData=gson.fromJson(bodyData, ContractInfoData.class);
            String conNo=contractInfoData.getContract_no();
            if(conNo!=null){
                Map<String,String> result=contractDAO.getContractInfo(conNo);  
                if (result!=null && conNo.equals(result.get("contractNo"))){
                    resMap.put("message","success");
                    resMap.put("contract_no",result.get("contractNo"));
                    resMap.put("service_str", result.get("serviceStr"));
                    resMap.put("mon_status", result.get("monStatus"));
                    status=HttpStatus.OK;
                }
                else {
                    status=HttpStatus.OK;
                }
                log.info("==> SELECT SUCCESS! // Contract_no :: " + contractInfoData.getContract_no());
            }
            else{
                resMap.put("message", "failure");
                log.info("==> SELECT FAILURE! // Contract_no :: " + contractInfoData.getContract_no());
            }
                           
        } catch (Exception e) {
            log.error(e.toString());
            log.error("==> bodyData :: ");
            log.error(bodyData); 
        }
        healthDao.selectContractInfoList();
        return new ResponseEntity<>(resMap, status);

    } 

    public ResponseEntity<Map<String, String>> updateContractInfo(String bodyData){
        log.info("[POST] CONTRACTINFO UPDATE ACCESS ");
        Map<String, String> resMap = new HashMap<>();
        resMap.put("message", "failure");
        status=HttpStatus.BAD_REQUEST;
        int result=0;
        JsonObject contracts = gson.fromJson(bodyData,JsonObject.class);
        JsonArray contractArr=contracts.get("contract_list").getAsJsonArray();   
        for (JsonElement contractElement : contractArr) { 
            try{
                ContractInfoData contractInfoData =gson.fromJson(contractElement,ContractInfoData.class);
                result=contractDAO.updateContractInfo(contractInfoData);
                if (result>0){
                    resMap.put("message", "success");
                    status=HttpStatus.OK;                 
                }
                else{
                    log.error("CONTRACTINFO UPDATE FAILURE" );
                }
            } catch(Exception e) {
                log.error(e.toString());
                log.error("==> bodyData :: ");
                log.error(bodyData);
            }
        }
        log.info("CONTRACTINFO UPDATE SUCCESS : "+contractArr.size());
        healthDao.selectContractInfoList();
        return new ResponseEntity<>(resMap, status);
    } 

    
    
}
