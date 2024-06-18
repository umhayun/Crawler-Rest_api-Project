package com.wizontech.adtcaps.service;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.annotation.Resource;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.wizontech.adtcaps.dao.PatternDAO;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class PatternService {

    @Autowired
    private PatternDAO patternDAO;

    @Autowired
    private PatternAvgServise patternAvgServise;

    @Resource(name = "industryMaskMap")
    Map<String, Map<String, String>> industryMaskMap;

    @Resource(name = "nvrMaskMap")
    Map<String, Map<String, String>> nvrMaskMap;

    @Resource(name = "cLAvgMap")
    Map<String, Map<String, String>> cLAvgMap;

    @Resource(name = "cLCountMap")
    Map<String, String> cLCountMap;

    HttpStatus status = HttpStatus.INTERNAL_SERVER_ERROR;
    Gson gson = new Gson();

    public ResponseEntity<Map<String, Object>> getPatternList() {
        // "CHECK_L": "[4,5,10,7]"
        List<Map<String, Object>> patternList = patternDAO.getPatternList();
        List<Map<String, Object>> paramList = new ArrayList<>();
        Map<String, Object> resMap = new HashMap<>();

        String checkLStr;
        String regex;
        String checkLArr[];
        int checkLArrInt[];

        if (patternList == null) {
            resMap.put("message", "failure");
            status = HttpStatus.BAD_REQUEST;
            log.error("==> patternList is null!");
        } else {
            for (Map<String, Object> pattern : patternList) {
                Map<String, Object> paramMap = new HashMap<>();

                try {
                    checkLStr = pattern.get("CHECK_L").toString();
                    regex = ".*[\\[\\]].*";
                    if (checkLStr.matches(regex)) {
                        checkLStr = checkLStr.replaceAll("\\[", "");
                        checkLStr = checkLStr.replaceAll("\\]", "");
                    }
                    // CHECK_L = [] 이면
                    if (checkLStr.equals("")) {
                        checkLArrInt = new int[0];
                        paramMap.put("CHECK_L", checkLArrInt);
                    } else {
                        checkLArr = checkLStr.split(",");
                        checkLArrInt = new int[checkLArr.length];
                        for (int i = 0; i < checkLArr.length; i++) {
                            checkLArrInt[i] = Integer.parseInt(checkLArr[i]);
                        }
                        paramMap.put("CHECK_L", checkLArrInt);
                    }

                    paramMap.put("PatternSEQ", pattern.get("PATTERNSEQ").toString());
                    paramMap.put("Type", pattern.get("TYPE").toString());
                    paramMap.put("Scope", pattern.get("SCOPE").toString());
                    paramMap.put("IndustryCode", pattern.get("INDUSTRYCODE").toString());
                    paramMap.put("NVRSN", pattern.get("NVRSN").toString());
                    paramMap.put("Category", pattern.get("CATEGORY").toString());
                    paramMap.put("Check_H", pattern.get("CHECK_H").toString());
                    paramMap.put("Check_L", pattern.get("CHECK_L").toString());
                    paramList.add(paramMap);

                } catch (Exception e) {
                    log.error(e.toString());
                    log.error("==> pattern :: " + pattern.toString());
                }
            }

            if (paramList.size() > 0) {
                resMap.put("PatternTotal", paramList);
                status = HttpStatus.OK;
            } else {
                resMap.put("message", "failure");
                status = HttpStatus.BAD_REQUEST;
                log.error("***** paramList is null!");
            }
        }

        return new ResponseEntity<>(resMap, status);
    }

    public ResponseEntity<Map<String, String>> insertPattern(String bodyData) {
        Map<String, String> resMap = new HashMap<>(); // 응답으로 보낼 Map
        Map<String, String> NMap = new HashMap<>(); // maskingMap에 담을 Map
        Map<String, String> LMap = new HashMap<>(); // cLAvgMap에 담을 Map
        Map<String, String> paramMap = new HashMap<>(); // DB에 저장할 Map

        resMap.put("message", "failure");
        status = HttpStatus.BAD_REQUEST;

        JsonObject jsonObj = null;
        String[] avgArr = null;
        String avgStr = null; // CHECK_L를 가져올 변수
        String patternSeq = null;
        String category = null;
        String type = null;
        String scope = null;
        String nvrsn = null;
        String industrycode = null;

        try {
            jsonObj = gson.fromJson(bodyData, JsonObject.class);

            patternSeq = jsonObj.get("PatternSEQ").getAsString();
            category = jsonObj.get("Category").getAsString();
            type = jsonObj.get("Type").getAsString();
            scope = jsonObj.get("Scope").getAsString();
            nvrsn = jsonObj.get("NVRSN").getAsString();
            industrycode = jsonObj.get("IndustryCode").getAsString();

            Date date = new Date();
            SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy-MM-dd");
            String currDate = simpleDateFormat.format(date);

            // DB에 저장할 Map
            paramMap.put("PATTERNSEQ", patternSeq);
            paramMap.put("TYPE", type);
            paramMap.put("CATEGORY", category);
            paramMap.put("SCOPE", scope);
            paramMap.put("NVRSN", nvrsn);
            paramMap.put("INDUSTRYCODE", industrycode);
            paramMap.put("CHECK_H", jsonObj.get("Check_H").getAsString());
            paramMap.put("CHECK_L", jsonObj.get("Check_L").getAsJsonArray().toString());
            paramMap.put("DATE_TIME", currDate);

            NMap.put("PATTERNSEQ", patternSeq);
            NMap.put("TYPE", type);
            NMap.put("CATEGORY", category);
            NMap.put("NVRSN", nvrsn);
            NMap.put("INDUSTRYCODE", industrycode);
            NMap.put("CHECK_H", jsonObj.get("Check_H").getAsString());
            NMap.put("DATE_TIME", currDate);

            LMap.put("CATEGORY", category);
            LMap.put("NVRSN", nvrsn);
            LMap.put("CHECK_L", jsonObj.get("Check_L").getAsJsonArray().toString());
            LMap.put("DATE_TIME", currDate);

            // 빅데이터 적용 - 평균값
            if (type.equals("N") && category.equals("A")) {
                double val = 0.0; // 빅데이터 설정값
                StringBuffer sb = new StringBuffer();
                if (scope.equals("I")) {
                    avgArr = patternAvgServise.getAvgArr("N", "industry_code", industrycode);
                    NMap.remove("NVRSN");
                } else if (scope.equals("M")) {
                    avgArr = patternAvgServise.getAvgArr("N", "ddns_mac", nvrsn);
                    NMap.remove("INDUSTRYCODE");
                }
                if (avgArr != null) {
                    for (int i = 0; i < avgArr.length; i++) {
                        if (val < Double.parseDouble(avgArr[i])) {
                            sb.append("1");
                        } else {
                            sb.append("0");
                        }
                    }
                    log.info("==> check_h :: " + sb.toString());
                    paramMap.put("CHECK_H", sb.toString());
                    NMap.put("CHECK_H", sb.toString());
                } else {
                    log.error("==> avgArr is null!");
                }
            } else if (type.equals("L") && category.equals("A")) {
                // 현재 날짜에 전날의 평균값을 구한 기록이 있다면 cLAvgMap 에서 데이터를 가져오기
                if (cLAvgMap.containsKey(nvrsn) && cLAvgMap.get(nvrsn).get("DATE_TIME").equals(currDate)) {
                    avgStr = cLAvgMap.get(nvrsn).get("CHECK_L");
                } else {
                    avgArr = patternAvgServise.getAvgArr("L", "ddns_mac", nvrsn);
                    avgStr = Arrays.toString(avgArr).replaceAll(" ", "");
                }
                log.info("==> avgStr :: " + avgStr);

                paramMap.put("CHECK_L", avgStr);
                LMap.put("CHECK_L", avgStr);
            }

            // pattern_api 테이블에 저장
            int result = patternDAO.insertPattern(paramMap);
            if (result == 1) {
                resMap.put("message", "success");
                status = HttpStatus.OK;
                log.info("==> insert success! // patternSeq :: " + patternSeq);

                // 각 hashmap과 masking 테이블에 저장
                if (type.equals("N") && scope.equals("I")) {
                    patternDAO.insertIndustryMasking(NMap);
                    industryMaskMap.put("N-" + industrycode, NMap);

                } else if (type.equals("N") && scope.equals("M")) {
                    patternDAO.insertNvrMasking(NMap);
                    nvrMaskMap.put("N-" + nvrsn, NMap);

                } else if (type.equals("L")) {
                    cLAvgMap.put(nvrsn, LMap);
                }
            } else {
                log.error("==> insert failure! // patternSeq :: " + patternSeq);
            }
        } catch (Exception e) {
            log.error(e.toString());
            log.error("==> bodyData :: ");
            log.error(bodyData);
        }

        return new ResponseEntity<>(resMap, status);
    }

    public ResponseEntity<Map<String, String>> updatePattern(String bodyData) {
        Map<String, String> resMap = new HashMap<>(); // 응답으로 보낼 Map
        Map<String, String> NMap = new HashMap<>(); // maskingMap에 담을 Map
        Map<String, String> LMap = new HashMap<>(); // cLAvgMap에 담을 Map
        Map<String, String> paramMap = new HashMap<>(); // DB에 저장할 Map

        resMap.put("message", "failure");
        status = HttpStatus.BAD_REQUEST;

        JsonObject jsonObj = null;
        String[] avgArr = null;
        String avgStr = null;
        String patternSeq = null;
        String category = null;
        String type = null;
        String scope = null;
        String nvrsn = null;
        String industrycode = null;

        try {
            jsonObj = gson.fromJson(bodyData, JsonObject.class);

            if (jsonObj == null) {
                resMap.put("message", "failure");
                log.error("==> jsonObj is null!");
                log.error("==> bodyData :: ");
                log.error(bodyData);
            } else {
                patternSeq = jsonObj.get("PatternSEQ").getAsString();
                category = jsonObj.get("Category").getAsString();
                type = jsonObj.get("Type").getAsString();
                scope = jsonObj.get("Scope").getAsString();
                nvrsn = jsonObj.get("NVRSN").getAsString();
                industrycode = jsonObj.get("IndustryCode").getAsString();

                Date date = new Date();
                SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy-MM-dd");
                String currDate = simpleDateFormat.format(date);

                paramMap.put("PATTERNSEQ", patternSeq);
                paramMap.put("TYPE", type);
                paramMap.put("CATEGORY", category);
                paramMap.put("SCOPE", scope);
                paramMap.put("NVRSN", nvrsn);
                paramMap.put("INDUSTRYCODE", industrycode);
                paramMap.put("CHECK_H", jsonObj.get("Check_H").getAsString());
                paramMap.put("CHECK_L", jsonObj.get("Check_L").getAsJsonArray().toString());
                paramMap.put("DATE_TIME", currDate);

                NMap.put("PATTERNSEQ", patternSeq);
                NMap.put("TYPE", type);
                NMap.put("CATEGORY", category);
                NMap.put("NVRSN", nvrsn);
                NMap.put("INDUSTRYCODE", industrycode);
                NMap.put("CHECK_H", jsonObj.get("Check_H").getAsString());
                NMap.put("DATE_TIME", currDate);

                LMap.put("CATEGORY", category);
                LMap.put("NVRSN", nvrsn);
                LMap.put("CHECK_L", jsonObj.get("Check_L").getAsJsonArray().toString());
                LMap.put("DATE_TIME", currDate);

                if (type.equals("N") && category.equals("A")) {
                    // 평균값 구하기
                    double val = 0.0; // 적용 기준 수치
                    StringBuffer sb = new StringBuffer();
                    if (scope.equals("I")) {
                        avgArr = patternAvgServise.getAvgArr("N", "industry_code", industrycode);
                        NMap.remove("NVRSN");
                    } else if (scope.equals("M")) {
                        avgArr = patternAvgServise.getAvgArr("N", "ddns_mac", nvrsn);
                        NMap.remove("INDUSTRYCODE");
                    }
                    if (avgArr != null) {
                        for (int i = 0; i < avgArr.length; i++) {
                            if (val < Double.parseDouble(avgArr[i])) {
                                sb.append("1");
                            } else {
                                sb.append("0");
                            }
                        }
                        // log.info("==> check_h :: " + sb.toString());
                        paramMap.put("CHECK_H", sb.toString());
                        NMap.put("CHECK_H", sb.toString());
                    } else {
                        log.error("==> avgCount is null!");
                    }
                } else if (type.equals("L") && category.equals("A")) {
                    // 현재 날짜에 전날의 평균값을 구한 기록이 있다면 cLAvgMap 에서 데이터를 가져오기
                    if (cLAvgMap.containsKey(nvrsn) && cLAvgMap.get(nvrsn).get("DATE_TIME").equals(currDate)) {
                        avgStr = cLAvgMap.get(nvrsn).get("CHECK_L");
                    } else {
                        avgArr = patternAvgServise.getAvgArr("L", "ddns_mac", jsonObj.get("NVRSN").getAsString());
                        avgStr = Arrays.toString(avgArr).replaceAll(" ", "");
                    }
                    paramMap.put("CHECK_L", avgStr);
                    LMap.put("CHECK_L", avgStr);
                }

                // pattern_api 테이블에 저장
                int result = patternDAO.updatePattern(paramMap);
                if (result == 1) {
                    resMap.put("message", "success");
                    status = HttpStatus.OK;
                    log.info("==> update success! // patternSeq :: " + patternSeq);

                    // 각 hashmap과 masking 테이블에 저장
                    if (type.equals("N") && scope.equals("I")) {
                        patternDAO.updateIndustryMasking(NMap);
                        industryMaskMap.put("N-" + industrycode, NMap);

                    } else if (type.equals("N") && scope.equals("M")) {
                        log.info("!!! nvrMaskMap success!");
                        patternDAO.updateNvrMasking(NMap);
                        nvrMaskMap.put("N-" + nvrsn, NMap);

                    } else if (type.equals("L")) {
                        cLAvgMap.put(nvrsn, LMap);
                    }
                } else {
                    log.info("==> update failure! // patternSeq :: " + patternSeq);
                }
            }
        } catch (Exception e) {
            log.error(e.toString());
            log.error("==> bodyData :: ");
            log.error(bodyData);
        }

        return new ResponseEntity<>(resMap, status);
    }

    public ResponseEntity<Map<String, String>> deletePattern(String bodyData) {
        Map<String, String> resMap = new HashMap<>();
        Map<String, String> patternMap = new HashMap<>();

        resMap.put("message", "failure");
        status = HttpStatus.BAD_REQUEST;

        JsonObject jsonObj = null;
        String patternSeq = null;
        String type = null;
        String scope = null;
        String nvrsn = null;
        String check_L = null;
        String industrycode = null;

        try {
            jsonObj = gson.fromJson(bodyData, JsonObject.class);
            if (jsonObj == null) {
                resMap.put("message", "failure");
                log.error("==> jsonObj is null!");
                log.error("==> bodyData :: ");
                log.error(bodyData);
            } else {
                patternSeq = jsonObj.get("PatternSEQ").getAsString();
                patternMap = patternDAO.getPattern(patternSeq);

                type = patternMap.get("TYPE").toString();
                scope = patternMap.get("SCOPE").toString();
                nvrsn = patternMap.get("NVRSN").toString();
                check_L = patternMap.get("CHECK_L").toString();
                industrycode = patternMap.get("INDUSTRYCODE").toString();

                int result = patternDAO.deletePattern(patternSeq);
                if (result == 1) {
                    resMap.put("message", "success");
                    status = HttpStatus.OK;
                    log.info("==> delete success! // patternSeq :: " + patternSeq);

                    if (type.equals("N") && scope.equals("I")) {
                        int resultM = patternDAO.deleteIndustryMasking(patternSeq);
                        if (resultM == 1) {
                            industryMaskMap.remove(type + "-" + industrycode);
                        } else {
                            log.info("==> delete failure! IndustryMasking // patternSeq :: " + patternSeq);
                        }
                    } else if (type.equals("N") && scope.equals("M")) {
                        int resultM = patternDAO.deleteNvrMasking(patternSeq);
                        if (resultM == 1) {
                            nvrMaskMap.remove(type + "-" + industrycode);
                        } else {
                            log.info("==> delete failure! NvrMasking // patternSeq :: " + patternSeq);
                        }
                    } else if (type.equals("L")) {
                        cLAvgMap.remove(nvrsn);

                        // cLCountArr => 모든 자릿수를 0으로 변경
                        String regex = ".*[\\[\\]].*";
                        if (check_L.matches(regex)) {
                            check_L = check_L.replaceAll("\\[", "");
                            check_L = check_L.replaceAll("\\]", "");
                        }
                        String[] strArr = check_L.split(",");

                        int[] cLCountArr = new int[strArr.length];
                        cLCountMap.put(nvrsn, Arrays.toString(cLCountArr));
                        log.info("==> cLCountMap reset! :: " + cLCountMap.get(nvrsn));
                    }
                } else {
                    log.error("==> delete failure! // patternSeq :: " + patternSeq);
                }
            }
        } catch (Exception e) {
            log.error(e.toString());
            log.error("==> bodyData :: ");
            log.error(bodyData);
        }

        return new ResponseEntity<Map<String, String>>(resMap, status);
    }
}