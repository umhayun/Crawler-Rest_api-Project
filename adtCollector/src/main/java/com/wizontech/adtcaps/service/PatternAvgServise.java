package com.wizontech.adtcaps.service;

import java.text.DecimalFormat;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.wizontech.adtcaps.dao.PatternAvgDAO;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class PatternAvgServise {

    @Value("${searchCount.avgValue}")
    private double avgValue;

    @Autowired
    private PatternAvgDAO patternAvgDAO;

    Gson gson = new Gson();

    public ResponseEntity<Map<String, Object>> patternAvg(String type, String key, String value) {
        HttpStatus status = HttpStatus.INTERNAL_SERVER_ERROR;

        Map<String, Object> result = null;
        Map<String, Object> resMap = new HashMap<>();
        String resultCode = "500";
        String resultBody = null;

        try {
            result = patternAvgDAO.getResultMap(type, key, value);
            // log.info("!!! result :: " + result.toString());

            resultCode = result.get("resultCode").toString();
            resultBody = result.get("resultBody").toString();
        } catch (Exception e) {
            log.error(e.toString());
        }

        log.info("==> resultCode: " + resultCode);
        // log.info("==> resultBody: " + resultBody);

        if (resultCode.equals("400")) {
            resMap.put("patternAvg", "failure");
            status = HttpStatus.BAD_REQUEST;
        } else if (resultCode.equals("200")) {
            status = HttpStatus.OK;

            if (type.equals("N")) {
                resMap.put("NetEnd_Aver", getAvgNet(resultBody));
            } else if (type.equals("L")) {
                resMap.put("Channel_Aver", getAvgLoss(resultBody));
            }
        }

        return new ResponseEntity<>(resMap, status);
    }

    // pattern_api에서 사용
    public String[] getAvgArr(String type, String key, String value) {
        Map<String, Object> result = patternAvgDAO.getResultMap(type, key, value);
        String resultBody = result.get("resultBody").toString();
        String[] avgArr = null;
        if (type.equals("N")) {
            avgArr = getAvgNet(resultBody);
        } else if (type.equals("L")) {
            avgArr = getAvgLoss(resultBody);
        }
        return avgArr;
    }

    public String[] getAvgNet(String resultBody) {
        long[] totalArr = new long[24];
        String[] avgArr = new String[24];

        JsonObject jsonObjBody = gson.fromJson(resultBody, JsonObject.class);
        JsonObject jsonObjAggr = jsonObjBody.get("aggregations").getAsJsonObject();
        JsonObject jsonObjReq = jsonObjAggr.get("request_count").getAsJsonObject();
        JsonArray jsonArrResult = jsonObjReq.get("buckets").getAsJsonArray();
        log.info("==> JsonArrCount size :: " + Integer.toString(jsonArrResult.size()));

        for (JsonElement result : jsonArrResult) {
            JsonObject JsonObjCount = result.getAsJsonObject();
            String keyAsString = JsonObjCount.get("key_as_string").toString();
            String dataTime = keyAsString.split("T")[1].split(":")[0];

            if (dataTime.startsWith("0")) {
                dataTime = dataTime.substring(1);
            }

            for (int i = 0; i < 24; i++) {
                if (dataTime.equals(Integer.toString(i))) {
                    totalArr[i] += JsonObjCount.get("doc_count").getAsLong();
                }
            }
        }

        log.info("==> avgValue :: " + avgValue);
        // 평균 구하기
        DecimalFormat df;
        for (int i = 0; i < totalArr.length; i++) {
            // log.info("==> totalArr" + i + " :: " + totalArr[i]);
            // avgArr[i] = totalArr[i] / avgValue;
            df = new DecimalFormat("0.0");
            avgArr[i] = df.format(totalArr[i] / avgValue);
        }
        log.info("==> avgArr :: " + Arrays.toString(avgArr));
        return avgArr;
    }

    public String[] getAvgLoss(String resultBody) {
        // log.info("==> resultBody :: " + resultBody);

        int lossCountArr[] = null;
        int alarmCountArr[] = null;

        String avgArr[] = null;
        String prevArr[] = null;
        String currArr[] = null;
        String currStr = null;

        JsonObject jsonObjBody = gson.fromJson(resultBody, JsonObject.class);
        JsonObject jsonObjHits = jsonObjBody.get("hits").getAsJsonObject();
        JsonArray jsonObjArr = jsonObjHits.get("hits").getAsJsonArray();
        log.info("==> JsonArrCount size :: " + Integer.toString(jsonObjArr.size()));

        JsonObject hits;
        JsonObject source;
        for (JsonElement jsonObj : jsonObjArr) {
            hits = jsonObj.getAsJsonObject();
            source = hits.get("_source").getAsJsonObject();
            currStr = source.get("ddns_camerausage").getAsString();
            if (!currStr.equals("")) {
                currArr = currStr.split("");

                if (prevArr == null) {
                    // log.info("==> prevArr is null!");
                    prevArr = currStr.split("");

                    // [0,0,0,0]
                    lossCountArr = new int[currArr.length];
                    alarmCountArr = new int[currArr.length];
                    avgArr = new String[currArr.length];

                    for (int i = 0; i < currArr.length; i++) {
                        if (currArr[i].equals("0")) {
                            lossCountArr[i] += 1;
                            alarmCountArr[i] += 1;
                        }
                    }
                } else {
                    // log.info("!!! prevArr :: " + Arrays.toString(prevArr));
                    for (int i = 0; i < currArr.length; i++) {
                        if (currArr[i].equals("0")) {
                            lossCountArr[i] += 1;
                        }
                        if (currArr[i].equals("0")
                                && Integer.parseInt(currArr[i]) + Integer.parseInt(prevArr[i]) == 1) {
                            alarmCountArr[i] += 1;
                        }
                    }
                    prevArr = currStr.split("");
                    // log.info("!!! prevArr :: " + Arrays.toString(prevArr));
                }
            }
        }
        log.info("==> lossCountArr :: " + Arrays.toString(lossCountArr));
        log.info("==> alarmCountArr :: " + Arrays.toString(alarmCountArr));

        int div;
        try {
            for (int i = 0; i < currArr.length; i++) {
                if (alarmCountArr[i] == 0) {
                    avgArr[i] = "0";
                } else {
                    div = lossCountArr[i] / alarmCountArr[i];
                    // log.info("==> div :: " + div);
                    avgArr[i] = Integer.toString(div);
                }
            }
        } catch (Exception e) {
            log.error(e.toString());
        }
        log.info("==> avgArr :: " + Arrays.toString(avgArr));

        return avgArr;
    }
}
