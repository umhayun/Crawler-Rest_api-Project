package com.wizontech.adtcaps.service;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import com.google.gson.Gson;
import com.wizontech.adtcaps.dao.ArgosDAO;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class ArgosService {
    HttpStatus status = HttpStatus.INTERNAL_SERVER_ERROR;
    Gson gson = new Gson();
    
    @Autowired
    ArgosDAO argosDAO;
    
    @SuppressWarnings("unchecked")
    public ResponseEntity<Map<String, String>> updateArgosSendStatus(String bodyData){
        
        Map<String, String> resMap = new HashMap<>();
        resMap.put("message", "failure");
        status=HttpStatus.BAD_REQUEST;
        Map<String,String> argos_status=new HashMap<String,String>();
        try {
            argos_status= gson.fromJson(bodyData,Map.class);
            int result=argosDAO.updateArgosSendStatus(argos_status);
            if (result>0){
                resMap.put("message","success");
                status=HttpStatus.OK;
                log.info("ArgosSendStatus  UPDATE SUCCESS // send_yn :: "+argos_status.get("send_yn"));
            }
            else{
                log.info("ArgosSendStatus  UPDATE FAILURE // send_sn :: "+argos_status.get("send_yn"));
            }
            
            
        } catch (Exception e) {
            log.error(e.toString());
            log.error("==> bodyData :: ");
            log.error(bodyData);
        }

        return new ResponseEntity<>(resMap, status);
    }

    public ResponseEntity<Map<String, String>> getArgosSendStatus(){
        log.info("[GET] SELECT ARGOS SEND STATUS ");
        Map<String, String> resMap = new HashMap<>();
        
        status=HttpStatus.BAD_REQUEST;
        try {
            resMap=argosDAO.getArgosSendStatus();
            if(resMap.size()>0){
                log.info("ARGOS STATUS SELECT SUCCESS");
            }

        } catch (Exception e) {
            log.error(e.toString());
        }
        return new ResponseEntity<>(resMap, status);
    }
    
    
}
