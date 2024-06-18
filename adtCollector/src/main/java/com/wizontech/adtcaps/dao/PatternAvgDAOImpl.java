package com.wizontech.adtcaps.dao;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Repository;

import com.wizontech.adtcaps.utils.ElasticApi;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Repository
public class PatternAvgDAOImpl implements PatternAvgDAO {

    @Value("${searchCount.avgValue}")
    private double avgValue;

    @Autowired
    private ElasticApi elasticApi;

    @Override
    public Map<String, Object> getResultMap(String type, String key, String value) {
        Date date = new Date();
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
        Calendar cal = Calendar.getInstance();
        // 오늘 날짜 세팅
        cal.setTime(date);
        // cal.add(Calendar.DATE, -1); // 테스트
        String today = sdf.format(cal.getTime());
        String startDay;
        String startDate;
        String endDate;
        String searchUrl = null;
        String jsonData = null;

        if (type.equals("N")) {
            // 평균 낼 날짜 세팅 (-21일)
            cal.add(Calendar.DATE, -(int) avgValue);
            startDay = sdf.format(cal.getTime());
            // log.info("==> startDay: " + startDay + " // today: " + today);

            startDate = startDay + "T00:00:00";
            endDate = today + "T00:00:00";
            // log.info("startDate :: " + startDate + " // endDate :: " + endDate);

            searchUrl = "adt_focus_*/_search?size=0";
            jsonData = "{\"sort\": \"log_timestamp\",\"query\": {\"bool\": {\"must\": {\"match\": {\"" + key + "\": \""
                    + value + "\"}}," +
                    "\"filter\": {\"range\": {\"log_timestamp\": {\"gte\": \"" + startDate + "\",\"lt\": \"" + endDate
                    + "\"}}}}}," +
                    "\"aggs\": {\"request_count\": {\"date_histogram\": {\"field\": \"log_timestamp\",\"calendar_interval\": \"hour\"}}}}";

        } else if (type.equals("L")) {
            // 평균 낼 날짜 세팅 (-1일)
            cal.add(Calendar.DATE, -1);
            startDay = sdf.format(cal.getTime());
            log.info("==> startDay: " + startDay + " // today: " + today);

            startDate = startDay + "T00:00:00";
            endDate = today + "T00:00:00";
            log.info("startDate :: " + startDate + " // endDate :: " + endDate);

            searchUrl = "adt_focus_*/_search?size=10000";
            jsonData = "{\"_source\": \"ddns_camerausage\"," +
                    "\"sort\": \"log_timestamp\",\"query\": {\"bool\": {\"must\": {\"match\": {\"" + key + "\": \""
                    + value + "\"}}," +
                    "\"filter\": {\"range\": {\"log_timestamp\": {\"gte\": \"" + startDate + "\",\"lt\": \"" + endDate
                    + "\"}}}}}}";
        }

        log.info("String query: GET " + searchUrl + jsonData);
        return elasticApi.callElasticApi("GET", searchUrl, jsonData);
    }
}