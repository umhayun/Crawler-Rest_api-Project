package com.wizontech.adtcaps.service;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import javax.annotation.Resource;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.wizontech.adtcaps.dao.IndustryDAO;
import com.wizontech.adtcaps.entity.IndustryData;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class IndustryService {

    @Autowired
    private IndustryDAO industryDAO;

    @Resource(name = "nvrMap")
    Map<String, Map<String, String>> nvrMap;

    HttpStatus status = HttpStatus.INTERNAL_SERVER_ERROR;
    Gson gson = new Gson();

    public ResponseEntity<Map<String, Object>> getIndustryList() {
        Map<String, Object> resMap = new HashMap<>();
        List<IndustryData> industryList = industryDAO.getIndustryList();
        List<Map<String, String>> paramList = new ArrayList<>();

        if (industryList.size() > 0) {
            for (IndustryData data : industryList) {
                Map<String, String> pMap = new HashMap<>();
                pMap.put("NVRSN", data.getNVRSN());
                pMap.put("IndustryCode", data.getIndustryCode());
                pMap.put("Gross", data.getGross());
                pMap.put("GVIP", data.getGVIP());
                paramList.add(pMap);
            }

            resMap.put("IndustryTotal", paramList);
            status = HttpStatus.OK;
        } else {
            resMap.put("message", "failure");
            status = HttpStatus.BAD_REQUEST;
            log.error("***** industryList is null!");
        }

        return new ResponseEntity<>(resMap, status);
    }

    @SuppressWarnings("unchecked")
    public ResponseEntity<Map<String, String>> insertAllIndustry(String bodyData) {
        JsonObject jsonObj = null;
        Map<String, String> resMap = new HashMap<>(); // 응답 Map
        Map<String, Object> insertMap = new HashMap<>(); // maybatis에 던질 Map
        List<Map<String, String>> insertList = new ArrayList<>();
        ; // maybatis에 던질 Map에 넣을 List
        List<Map<String, String>> bodyDataList = new ArrayList<>();
        ; // bodyData List

        resMap.put("message", "failure");
        status = HttpStatus.BAD_REQUEST;

        int result = 0;
        try {
            jsonObj = gson.fromJson(bodyData, JsonObject.class);
            bodyDataList = (List<Map<String, String>>) gson.fromJson(jsonObj.get("IndustryTotal").toString(),
                    List.class);

            if (bodyDataList.size() > 0) {
                // 저장 전 전체 삭제
                industryDAO.deleteAllIndustry();

                // 날짜 포함해서 nvrMap 에 저장 그리고 insertList 에 add
                Date date = new Date();
                SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

                String currTime = simpleDateFormat.format(date);
                for (Map<String, String> element : bodyDataList) {
                    Map<String, String> vMap = new HashMap<>();
                    vMap.put("NVRSN", element.get("NVRSN"));
                    vMap.put("INDUSTRYCODE", element.get("IndustryCode"));
                    vMap.put("GROSS", element.get("Gross"));
                    vMap.put("GVIP", element.get("GVIP"));
                    vMap.put("DATE_TIME", currTime);
                    insertList.add(vMap);
                }
                insertMap.put("insertList", insertList);
                result = industryDAO.insertAllIndustry(insertMap);

                if (result > 0) {
                    for (Map<String, String> element : bodyDataList) {
                        Map<String, String> vMap = new HashMap<>();
                        vMap.put("NVRSN", element.get("NVRSN"));
                        vMap.put("INDUSTRYCODE", element.get("IndustryCode"));
                        vMap.put("GROSS", element.get("Gross"));
                        vMap.put("GVIP", element.get("GVIP"));
                        vMap.put("DATE_TIME", currTime);
                        nvrMap.put(element.get("NVRSN"), vMap);
                    }

                    // nvrMap에서 오늘 날짜 아닌 것 지우기
                    for (Iterator<String> iter = nvrMap.keySet().iterator(); iter.hasNext();) {
                        String key = iter.next();
                        // log.info("==> key :: " + key);
                        if (!nvrMap.get(key).get("DATE_TIME").split(" ")[0].equals(currTime.split(" ")[0])) {
                            iter.remove();
                        }
                    }
                    log.info("==> nvrMap size :: " + nvrMap.size());
                    // log.info("==> nvrMap size :: " + nvrMap.size() + " :: " + nvrMap.toString());

                    resMap.put("message", "success");
                    status = HttpStatus.OK;
                    log.info("==> insert success! // result :: " + result);

                } else {
                    log.error("==> insert failure! // result :: " + result);
                }
            }
        } catch (Exception e) {
            log.error(e.toString());
            log.error("******* bodyData :: ");
            log.error(bodyData);
        }

        return new ResponseEntity<>(resMap, status);
    }

    @SuppressWarnings("unchecked")
    public ResponseEntity<Map<String, String>> updateIndustry(String bodyData) {
        Map<String, String> resMap = new HashMap<>();

        resMap.put("message", "failure");
        status = HttpStatus.BAD_REQUEST;

        try {
            Map<String, String> industryMap = new ObjectMapper().readValue(bodyData, HashMap.class);
            int result = industryDAO.updateIndustry(industryMap);

            if (result == 1) {
                resMap.put("message", "success");
                status = HttpStatus.OK;
                log.info("==> update success! // NVRSN :: " + industryMap.get("NVRSN"));

                Date date = new Date();
                SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
                Calendar cal = Calendar.getInstance();
                cal.setTime(date);
                String currTime = simpleDateFormat.format(cal.getTime());

                Map<String, String> vMap = new HashMap<>();
                vMap.put("NVRSN", industryMap.get("NVRSN"));
                vMap.put("INDUSTRYCODE", industryMap.get("IndustryCode"));
                vMap.put("GROSS", industryMap.get("Gross"));
                vMap.put("GVIP", industryMap.get("GVIP"));
                vMap.put("DATE_TIME", currTime);
                nvrMap.put(industryMap.get("NVRSN"), vMap);
                // log.info("==> nvrMap" + nvrMap.toString());
            } else {
                log.info("==> update failure! // NVRSN :: " + industryMap.get("NVRSN"));
            }
        } catch (Exception e) {
            log.error(e.toString());
            log.error("==> bodyData :: ");
            log.error(bodyData);
        }

        return new ResponseEntity<>(resMap, status);
    }

    public ResponseEntity<Map<String, String>> deleteIndustry(String bodyData) {
        Map<String, String> resMap = new HashMap<>();

        resMap.put("message", "failure");
        status = HttpStatus.BAD_REQUEST;

        try {
            IndustryData industryData = gson.fromJson(bodyData, IndustryData.class);
            String nvrsn = industryData.getNVRSN();
            int result = industryDAO.deleteIndustry(nvrsn);

            if (result == 1) {
                resMap.put("message", "success");
                status = HttpStatus.OK;
                nvrMap.remove(nvrsn);
                log.info("==> delete success! // NVRSN :: " + nvrsn);
                // log.info("==> nvrMap size :: " + nvrMap.size());
            } else {
                log.error("==> delete failure! // NVRSN :: " + nvrsn);
                // log.info("==> nvrMap size :: " + nvrMap.size());
            }
        } catch (Exception e) {
            log.error(e.toString());
            log.error("==> bodyData :: ");
            log.error(bodyData);
        }

        return new ResponseEntity<Map<String, String>>(resMap, status);
    }
}