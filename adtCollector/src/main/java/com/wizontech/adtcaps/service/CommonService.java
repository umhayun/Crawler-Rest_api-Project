package com.wizontech.adtcaps.service;

import java.util.Map;

import java.util.Date;
import java.util.HashMap;
import java.text.ParseException;
import java.text.SimpleDateFormat;

import org.springframework.stereotype.Service;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class CommonService {

    public Map<String, String> getDateTime(String dateKey, String timeKey) {
        Map<String, String> paramMap = new HashMap<>();
        long currTime = System.currentTimeMillis();
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        String logDate = dateFormat.format(currTime);
        String[] logDateArray = logDate.split(" ");
        String date = logDateArray[0];
        String time = logDateArray[1];
        paramMap.put(dateKey, date);
        paramMap.put(timeKey, time);
        return paramMap;
    }

    public Map<String, String> setIssueDate(String dateKey, String timeKey, String log_date) {
        Map<String, String> paramMap = new HashMap<>();
        long parseDate = Long.parseLong(log_date);
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyyMMdd HHmmss");
        String logDate = dateFormat.format(parseDate * 1000);
        String[] logDateArray = logDate.split(" ");
        String date = logDateArray[0];
        String time = logDateArray[1];
        paramMap.put(dateKey, date);
        paramMap.put(timeKey, time);
        return paramMap;
    }

    public Map<String, String> putFailureData(String uid, String sn, String log_date, String fault_code,
            String fault_type, String fault_desc, String camera_type, String modelNm, String firmVer) {
        Map<String, String> paramMap = new HashMap<>();
        paramMap.putAll(setIssueDate("ISSUE_DATE", "ISSUE_TIME", log_date));
        paramMap.put("UID", uid);
        paramMap.put("SN", sn);
        paramMap.put("LOG_DATE", log_date);
        paramMap.put("SIGNAL_TYPE", "E");
        paramMap.put("EQUIPMENT_TYPE", "D");
        paramMap.put("FAULT_CODE", fault_code);
        paramMap.put("DDNS_CAMERAUSAGE", null);
        paramMap.put("FAULT_TYPE", fault_type);
        paramMap.put("FAULT_DESC", fault_desc);
        paramMap.put("CAMERA_TYPE", camera_type);
        paramMap.put("SEND_YN", "N");
        paramMap.put("MODEL_NM", modelNm);
        paramMap.put("FIRM", firmVer);
        return paramMap;
    }

    public Map<String, String> putFailureDataCL(String uid, String sn, String log_date, String fault_code,
            String fault_type, String fault_desc, String camera_type, String ddns_camerausage, String modelNm,
            String firmVer) {
        Map<String, String> paramMap = new HashMap<>();
        paramMap.putAll(setIssueDate("ISSUE_DATE", "ISSUE_TIME", log_date));
        paramMap.put("UID", uid);
        paramMap.put("SN", sn);
        paramMap.put("LOG_DATE", log_date);
        paramMap.put("SIGNAL_TYPE", "E");
        paramMap.put("EQUIPMENT_TYPE", "D");
        paramMap.put("FAULT_CODE", fault_code);
        paramMap.put("DDNS_CAMERAUSAGE", ddns_camerausage);
        paramMap.put("FAULT_TYPE", fault_type);
        paramMap.put("FAULT_DESC", fault_desc);
        paramMap.put("CAMERA_TYPE", camera_type);
        paramMap.put("SEND_YN", "N");
        paramMap.put("MODEL_NM", modelNm);
        paramMap.put("FIRM", firmVer);
        return paramMap;
    }

    public Map<String, String> putRecoveryData(Map<String, Map<String, String>> failureMaps, String key) {
        Map<String, String> paramMap = new HashMap<>();
        paramMap.putAll(failureMaps.get(key));
        paramMap.putAll(getDateTime("UPDATE_DATE", "UPDATE_TIME"));
        paramMap.replace("SIGNAL_TYPE", "R");
        return paramMap;
    }

    public long getDateInterval(String regDate) {
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy.MM.dd HH:mm");
        long currTime = System.currentTimeMillis() / 1000;
        Date date;
        long endTime;
        long recInterval = 0;
        try {
            date = simpleDateFormat.parse(regDate);
            endTime = date.getTime() / 1000;
            recInterval = currTime - endTime;

        } catch (ParseException e) {
            log.error(e.toString());
        }
        return recInterval;
    }

    public long getTimeInterval(long regTime) {
        long currTime = System.currentTimeMillis() / 1000;
        long interval = currTime - regTime;
        return interval;
    }

    public long getMillisecond(String regDate) {
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy.MM.dd HH:mm");
        Date date;
        long millisecond = 0;
        try {
            date = simpleDateFormat.parse(regDate);
            millisecond = date.getTime() / 1000;

        } catch (ParseException e) {
            log.error(e.toString());
        }
        return millisecond;
    }

}