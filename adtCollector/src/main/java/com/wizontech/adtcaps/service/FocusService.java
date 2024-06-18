package com.wizontech.adtcaps.service;

import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;
import java.util.Map;
import java.util.HashMap;

import javax.annotation.Resource;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.wizontech.adtcaps.dao.CollectDao;
import com.wizontech.adtcaps.dao.HealthDaoImpl;
import com.wizontech.adtcaps.utils.FileUtil;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@EnableScheduling
@Service("FocusService")
public class FocusService implements CollectDao {

    @Autowired
    private FileUtil fileUtil;

    @Autowired
    Map<String, String> focusMap;

    @Resource(name = "cLCountMap")
    Map<String, String> cLCountMap;

    @Resource(name = "nvrMap")
    Map<String, Map<String, String>> nvrMap;

    @Resource(name = "industryMaskMap")
    Map<String, Map<String, String>> industryMaskMap;

    @Resource(name = "nvrMaskMap")
    Map<String, Map<String, String>> nvrMaskMap;

    @Resource(name = "cLAvgMap")
    Map<String, Map<String, String>> cLAvgMap;

    @Resource(name = "conditionMap")
    Map<String, Map<String, String>> conditionMap;

    @Resource(name = "equipmentInfoMap")
    Map<String, Map<String, String>> equipmentInfoMap;

    @Resource(name = "contractInfoMap")
    Map<String, Map<String, String>> contractInfoMap;

    @Autowired
    private CommonService commonService;

    @Autowired
    private HealthDaoImpl healthDao;

    @Resource(name = "failureMap")
    Map<String, Map<String, String>> failureMap;

    @Override
    public void writeJsonToFile(String jsonStr) {

        fileUtil.writeFile("focus", jsonStr);
    }

    Gson gson = new Gson();

    public Map<String, String> getEquipmentInfo(String sn) {
        Map<String, String> equipmentInfo = equipmentInfoMap.get(sn);

        if (equipmentInfo == null) {
            return null;
        }

        String contractNo = "";
        String accountNo = "";
        String serviceStr = "";
        int monStatus = -1;

        try {
            contractNo = equipmentInfo.get("contractNo");
            accountNo = equipmentInfo.get("accountNo");
            serviceStr = "";
        } catch (Exception e) {
            return null;
        }

        Map<String, String> contractInfo = contractInfoMap.get(contractNo);
        if (contractInfo == null) {
            return null;
        }

        try {
            serviceStr = contractInfo.get("serviceStr");
            monStatus = Integer.parseInt(contractInfo.get("monStatus"));
        } catch (Exception e) {
            return null;
        }

        if ((serviceStr.indexOf("A01") < 0 && serviceStr.indexOf("A02") < 0) ||
                (monStatus != 1 && monStatus != 0)) {
            return null;
        }

        Map<String, String> paramMap = new HashMap<String, String>();
        paramMap.put("CONTRACT_NO", contractNo);
        paramMap.put("ACCOUNT_NO", accountNo);
        paramMap.put("SERVICE_STR", serviceStr);

        return paramMap;
    }

    @Override
    public ResponseEntity<String> getData(String bodyData) {
        log.info("POST /focus received");
        HttpStatus status = HttpStatus.INTERNAL_SERVER_ERROR;

        int resultCount = 0;

        JsonObject jsonObj = null;
        JsonArray dataArr = null;
        String serverId;
        try {
            jsonObj = gson.fromJson(bodyData, JsonObject.class);
            dataArr = jsonObj.get("data").getAsJsonArray();
            serverId = jsonObj.get("server_id").getAsString();

        } catch (Exception e) {
            status = HttpStatus.BAD_REQUEST;
            log.error(e.toString());
            log.error("bodyData :: ");
            log.error(bodyData);

            return new ResponseEntity<>(status);
        }
        log.info("dataArrSize :: " + dataArr.size());

        if (dataArr.size() == 0) {
            log.error("dataArr is empty");
            log.error("bodyData :: ");
            log.error(bodyData);

        } else {
            String key = "";
            String mac = "";
            String uid = "";
            JsonObject prevObj = null;
            JsonObject currObj;
            long interval = 0;
            long prevTime = 0;
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss");
            String currTimstamp;
            long currTime;

            for (JsonElement dataElement : dataArr) {
                try {
                    currObj = dataElement.getAsJsonObject();

                    mac = currObj.get("ddns_mac").getAsString().toUpperCase();
                    uid = currObj.get("ddns_uid").getAsString().toUpperCase();
                    if (uid.equals("")) {
                        // log.info("*** uid is empty // mac :: " + mac);
                    } else {
                        currTime = System.currentTimeMillis() / 1000; // log_date
                        currTimstamp = sdf.format(currTime * 1000); // log_timestamp

                        currObj.addProperty("log_date", Long.toString(currTime));
                        currObj.addProperty("log_timestamp", currTimstamp);
                        currObj.addProperty("server_id", serverId);

                        // nvrMap에 키가 있으면 데이터 가져와서 add, 없으면 공백 넣기
                        if (nvrMap.containsKey(mac)) {
                            currObj.addProperty("industry_code", nvrMap.get(mac).get("INDUSTRYCODE"));
                            currObj.addProperty("gross", nvrMap.get(mac).get("GROSS"));
                            currObj.addProperty("gvip", nvrMap.get(mac).get("GVIP"));
                        } else {
                            currObj.addProperty("industry_code", "");
                            currObj.addProperty("gross", "");
                            currObj.addProperty("gvip", "");
                        }

                        // 장애|복구 판단
                        key = uid + "||" + mac;
                        if (focusMap.containsKey(key)) {
                            prevObj = gson.fromJson(focusMap.get(key), JsonObject.class);
                        }
                        failureCondition(currObj, prevObj);
                        if (prevObj != null) {
                            prevTime = prevObj.get("log_date").getAsLong();
                            interval = currTime - prevTime;
                            log.debug(key + " // interval :: " + interval);
                            if (interval < 0) {
                                log.info("interval :: " + currTime + " - " + prevTime + " = " + interval
                                        + " // key :: " + key);
                            }
                        } else {
                            log.debug(key + " // firstInsert");
                        }
                        currObj.addProperty("data_interval", interval);

                        writeJsonToFile(currObj.toString());
                        focusMap.put(key, currObj.toString());
                        status = HttpStatus.OK;
                        resultCount += 1;
                    }

                } catch (Exception e) {
                    status = HttpStatus.BAD_REQUEST;
                    log.error(e.toString());
                    log.error("dataElement :: " + dataElement.toString());
                }
            }
        }
        log.info("Status :: " + status + " // Result Count: " + resultCount);

        return new ResponseEntity<>(status);
    }

    @Override
    public void failureCondition(JsonObject currObj, JsonObject prevObj) {
        // log.info("!!! conditionMap: " + conditionMap);

        String uid = currObj.get("ddns_uid").getAsString().toUpperCase();
        String sn = currObj.get("ddns_mac").getAsString().toUpperCase();
        String log_date = currObj.get("log_date").getAsString();
        String modelNm = currObj.get("ddns_model").getAsString();
        String firmVer = currObj.get("ddns_firm").getAsString();
        String key;

        Map<String, String> equipInfo = getEquipmentInfo(sn);
        if (equipInfo == null) {
            return;
        }

        // HDD오류(1)
        key = uid + "||" + sn + "||" + "1" + "||" + "001";
        String ddns_hdd = currObj.get("ddns_hdd").getAsString();
        char first_num = 'N';
        int other_num = 0;
        if (!ddns_hdd.equals("")) {
            first_num = ddns_hdd.charAt(0);
            other_num = ddns_hdd.indexOf("1");
        }

        String allHddType = "Y";
        if (conditionMap.containsKey("allHddType")) {
            allHddType = conditionMap.get("allHddType").get("HDD_TYPE");
        }
        // log.info("!!! allHddType: " + allHddType);

        if (conditionMap.containsKey("hdd-" + sn)) {
            if (!conditionMap.get("hdd-" + sn).get("HDD_TYPE").equals("N")) {
                // 장애 판단
                if (ddns_hdd.charAt(0) != '2' && !failureMap.containsKey(key)) {
                    Map<String, String> paramMap = commonService.putFailureData(uid, sn, log_date, "001", "1",
                            "hddFault", "1", modelNm, firmVer);
                    paramMap.putAll(equipInfo);
                    int result = healthDao.insertFailure(paramMap, key);
                    if (result == 1) {
                        log.info("==> failure  // hdd :: " + ddns_hdd + " // key :: " + key);
                    } else {
                        log.error("*** failure // key :: " + key);
                    }
                } else if (ddns_hdd.charAt(0) == '2' && failureMap.containsKey(key)) {
                    Map<String, String> paramMap = commonService.putRecoveryData(failureMap, key);
                    int result = healthDao.insertRecovery(paramMap, key);
                    if (result == 1) {
                        log.info("==> recovery // hdd :: " + ddns_hdd + " // key :: " + key);
                    } else {
                        log.error("*** recovery // key :: " + key);
                    }
                }
            }
        } else {
            if (allHddType.equals("Y")) {
                // 장애 판단
                if (ddns_hdd.charAt(0) != '2' && !failureMap.containsKey(key)) {
                    Map<String, String> paramMap = commonService.putFailureData(uid, sn, log_date, "001", "1",
                            "hddFault", "1", modelNm, firmVer);
                    paramMap.putAll(equipInfo);

                    int result = healthDao.insertFailure(paramMap, key);
                    if (result == 1) {
                        log.info("==> failure  // hdd :: " + ddns_hdd + " // key :: " + key);
                    } else {
                        log.error("*** failure // key :: " + key);
                    }
                } else if (ddns_hdd.charAt(0) == '2' && failureMap.containsKey(key)) {
                    Map<String, String> paramMap = commonService.putRecoveryData(failureMap, key);
                    int result = healthDao.insertRecovery(paramMap, key);
                    if (result == 1) {
                        log.info("==> recovery // hdd :: " + ddns_hdd + " // key :: " + key);
                    } else {
                        log.error("*** recovery // key :: " + key);
                    }
                }
            }
        }

        // 채널로스(4)
        if (currObj.has("ddns_camerausage") && !currObj.get("ddns_camerausage").getAsString().equals("")) {
            // cLAvgMap => 채널별 채널로스 전날의 평균값
            // {"90DA6A06B79E": {"CATEGORY":"C", "CHECK_L": "[2,6,5,3,5,7,3,10]"},
            // "DATE_TIME": "2021-09-10"}
            // {"90DA6A0004B4": {"CATEGORY":"A", "CHECK_L": "[4,5,10,7]"}, "DATE_TIME":
            // "2021-09-10"}
            String ddns_camerausage = currObj.get("ddns_camerausage").getAsString();
            String currArr[] = ddns_camerausage.split("");

            // prevArr
            String prevBody = null;
            String prevArr[] = null;
            if (focusMap.containsKey(uid + "||" + sn)) {
                prevBody = focusMap.get(uid + "||" + sn);
                String prev_camerausage = null;
                if (prevBody != null) {
                    prev_camerausage = prevObj.get("ddns_camerausage").getAsString();
                    if (!prev_camerausage.equals("")) {
                        prevArr = prev_camerausage.split("");
                    }
                }
            }

            // 채널로스 전체 감시 유무
            String allLossYN = "Y";
            if (conditionMap.containsKey("allLossYN")) {
                allLossYN = conditionMap.get("allLossYN").get("LOSS_YN");
            }
            // log.info("!!! allLossYN :: " + allLossYN);

            // --------------------------------------------------- 패턴 등록이 있을 시
            if (cLAvgMap.containsKey(sn)) {
                // cLAvgMap에서 패턴 데이터 가져오기
                String avgStr = cLAvgMap.get(sn).get("CHECK_L").toString();
                // "[", "]" 제거
                String regex = ".*[\\[\\]].*";
                if (avgStr.matches(regex)) {
                    avgStr = avgStr.replaceAll("\\[", "");
                    avgStr = avgStr.replaceAll("\\]", "");
                }
                String strArr[] = avgStr.split(",");
                //
                int avgArr[] = new int[currArr.length];
                int cLCountArr[] = new int[currArr.length];

                // avgArr에 패턴 데이터 담기
                if (currArr.length > strArr.length) {
                    // log.info("==> pattern ddns_camerausage sizes are different!");
                    for (int i = 0; i < strArr.length; i++) {
                        avgArr[i] = Integer.parseInt(strArr[i]);
                    }
                } else {
                    for (int i = 0; i < currArr.length; i++) {
                        avgArr[i] = Integer.parseInt(strArr[i]);
                    }
                }
                log.info("==> avgArr :: " + Arrays.toString(avgArr) + ", sn :: " + sn);

                // LOSS_YN = "Y"
                if (allLossYN.equals("Y")) {
                    if (conditionMap.containsKey("loss-" + sn)
                            && conditionMap.get("loss-" + sn).get("LOSS_YN").equals("N")) {
                        // log.info("패턴 등록 있음, 조건 등록 N - 감지 안함");
                    } else {
                        // log.info("전체 Y ==> 패턴 등록 있음, 조건 등록 Y or 조건 등록 없음 - 패턴 감지");

                        // 기존 데이터가 없다면
                        if (prevArr == null) {
                            for (int i = 0; i < currArr.length; i++) {
                                if (currArr[i].equals("0")) {
                                    cLCountArr[i] += 1;
                                }
                                // 평균값(avgArr)보다 채널로스 count(cLCountArr)가 크면 장애 처리
                                if (cLCountArr[i] > avgArr[i]) {
                                    failureCL(i, uid, sn, log_date, ddns_camerausage, modelNm, firmVer);
                                }
                            }
                            // log.info("==> cLCountArr :: " + Arrays.toString(cLCountArr));
                            cLCountMap.put(sn, Arrays.toString(cLCountArr));
                            log.info("==> cLCountMap :: " + cLCountMap.get(sn) + ", cmr :: " + ddns_camerausage
                                    + ", sn :: " + sn);

                            // 기존 데이터가 있다면
                        } else {
                            // cLCountMap 에서 데이터 가져오기
                            String countStr = null;
                            if (cLCountMap.containsKey(sn)) {
                                countStr = cLCountMap.get(sn);
                            }
                            if (countStr != null) {
                                // "[", "]", 공백 제거
                                if (countStr.matches(regex)) {
                                    countStr = countStr.replaceAll("\\[", "");
                                    countStr = countStr.replaceAll("\\]", "");
                                }
                                countStr = countStr.replaceAll(" ", "");
                                String[] countStrArr = countStr.split(",");

                                if (currArr.length > countStrArr.length) {
                                    cLCountArr = new int[currArr.length];
                                    for (int i = 0; i < countStrArr.length; i++) {
                                        cLCountArr[i] = Integer.parseInt(countStrArr[i]);
                                    }
                                    // log.info("==> get cLCountArr :: " + Arrays.toString(cLCountArr));
                                } else {
                                    for (int i = 0; i < currArr.length; i++) {
                                        cLCountArr[i] = Integer.parseInt(countStrArr[i]);
                                    }
                                    // log.info("==> get cLCountArr :: " + Arrays.toString(cLCountArr));
                                }

                                // 장애 판단
                                for (int i = 0; i < currArr.length; i++) {
                                    if (currArr[i].equals("0")) {
                                        // 현재 값이 "0"이라면 배열에 (cLCountArr) 카운트 올리기
                                        cLCountArr[i] += 1;

                                        // 평균값보다 채널로스 count가 크면 장애 처리
                                        if (cLCountArr[i] > avgArr[i]) {
                                            failureCL(i, uid, sn, log_date, ddns_camerausage, modelNm, firmVer);
                                        }
                                    } else if (currArr[i].equals("1") && !ddns_camerausage.contains("0")) {
                                        cLCountArr[i] = 0;
                                        recoveryCL(i, uid, sn, log_date, ddns_camerausage);
                                    }
                                }
                                // log.info("==> cLCountArr :: " + Arrays.toString(cLCountArr));
                                cLCountMap.put(sn, Arrays.toString(cLCountArr));
                                log.info("==> cLCountMap :: " + cLCountMap.get(sn) + ", cmr :: " + ddns_camerausage
                                        + ", sn :: " + sn);
                            } else {
                                log.error("*** countStr is null / sn :: " + sn);
                                ;
                            }
                        }
                    }
                } else {
                    if (conditionMap.containsKey("loss-" + sn)
                            && conditionMap.get("loss-" + sn).get("LOSS_YN").equals("Y")) {
                        // log.info("전체 N ==> 패턴 등록 있음, 조건 등록 있음 - 패턴 감지");

                        // 기존 데이터가 없다면
                        if (prevArr == null) {
                            for (int i = 0; i < currArr.length; i++) {
                                if (currArr[i].equals("0")) {
                                    cLCountArr[i] += 1;
                                }
                                // 평균값(avgArr)보다 채널로스 count(cLCountArr)가 크면 장애 처리
                                if (cLCountArr[i] > avgArr[i]) {
                                    failureCL(i, uid, sn, log_date, ddns_camerausage, modelNm, firmVer);
                                }
                            }
                            // log.info("==> cLCountArr :: " + Arrays.toString(cLCountArr));
                            cLCountMap.put(sn, Arrays.toString(cLCountArr));
                            log.info("==> cLCountMap :: " + cLCountMap.get(sn) + ", cmr :: " + ddns_camerausage
                                    + ", sn :: " + sn);

                            // 기존 데이터가 있다면
                        } else {
                            // cLCountMap 에서 데이터 가져오기
                            String countStr = null;
                            if (cLCountMap.containsKey(sn)) {
                                countStr = cLCountMap.get(sn);
                            }
                            if (countStr != null) {
                                // "[", "]", 공백 제거
                                if (countStr.matches(regex)) {
                                    countStr = countStr.replaceAll("\\[", "");
                                    countStr = countStr.replaceAll("\\]", "");
                                }
                                countStr = countStr.replaceAll(" ", "");
                                String[] countStrArr = countStr.split(",");

                                if (currArr.length > countStrArr.length) {
                                    cLCountArr = new int[currArr.length];
                                    for (int i = 0; i < countStrArr.length; i++) {
                                        cLCountArr[i] = Integer.parseInt(countStrArr[i]);
                                    }
                                    // log.info("==> get cLCountArr :: " + Arrays.toString(cLCountArr));
                                } else {
                                    for (int i = 0; i < currArr.length; i++) {
                                        cLCountArr[i] = Integer.parseInt(countStrArr[i]);
                                    }
                                    // log.info("==> get cLCountArr :: " + Arrays.toString(cLCountArr));
                                }

                                // 장애 판단
                                for (int i = 0; i < currArr.length; i++) {
                                    if (currArr[i].equals("0")) {
                                        // 현재 값이 "0"이라면 배열에 (cLCountArr) 카운트 올리기
                                        cLCountArr[i] += 1;

                                        // 평균값보다 cLCount 가 크면 장애 처리
                                        if (cLCountArr[i] > avgArr[i]) {
                                            failureCL(i, uid, sn, log_date, ddns_camerausage, modelNm, firmVer);
                                        }
                                    } else if (currArr[i].equals("1") && !ddns_camerausage.contains("0")) {
                                        cLCountArr[i] = 0;
                                        recoveryCL(i, uid, sn, log_date, ddns_camerausage);
                                    }
                                }
                                // log.info("==> cLCountArr :: " + Arrays.toString(cLCountArr));
                                cLCountMap.put(sn, Arrays.toString(cLCountArr));
                                log.info("==> cLCountMap :: " + cLCountMap.get(sn) + ", cmr :: " + ddns_camerausage
                                        + ", sn :: " + sn);
                            } else {
                                log.error("*** countStr is null / sn :: " + sn);
                                ;
                            }
                        }
                    }
                }
                // --------------------------------------------------- 패턴 등록이 없을 시
            } else if (!cLAvgMap.containsKey(sn)) {
                if (allLossYN.equals("Y")) {
                    if (conditionMap.containsKey("loss-" + sn)
                            && conditionMap.get("loss-" + sn).get("LOSS_YN").equals("N")) {
                        // log.info("패턴 등록 없음, 조건 등록 N - 감지 안함");
                    } else {

                        // log.info("전체 Y ==> 패턴 등록 없음, 조건 등록 Y or 조건 등록 없음 - 일반 감지");
                        for (int i = 0; i < currArr.length; i++) {
                            // 기존 ddns_camerausage 값에 변화가 있다면
                            if (currArr[i].equals("0")) {
                                failureCL(i, uid, sn, log_date, ddns_camerausage, modelNm, firmVer);
                            } else if (!currArr[i].equals("0") && !ddns_camerausage.contains("0")) {
                                recoveryCL(i, uid, sn, log_date, ddns_camerausage);
                            }
                        }
                    }
                } else {
                    if (conditionMap.containsKey("loss-" + sn)
                            && conditionMap.get("loss-" + sn).get("LOSS_YN").equals("Y")) {
                        // log.info("!!! 전체 N ==> 패턴 등록 없음, 조건 등록 Y - 일반 감지");
                        for (int i = 0; i < currArr.length; i++) {
                            if (currArr[i].equals("0")) {
                                failureCL(i, uid, sn, log_date, ddns_camerausage, modelNm, firmVer);
                            } else if (!currArr[i].equals("0") && !ddns_camerausage.contains("0")) {
                                recoveryCL(i, uid, sn, log_date, ddns_camerausage);
                            }
                        }
                    }
                }
            }
        }

        // 네트워크 단선(2)의 복구 조건
        key = uid + "||" + sn + "||" + "2" + "||" + "001";
        if (failureMap.containsKey(key)) {
            Map<String, String> paramMap = commonService.putRecoveryData(failureMap, key);
            int result = healthDao.insertRecovery(paramMap, key);
            if (result == 1) {
                log.info("==> recovery // net // key :: " + key);
            } else {
                log.error("*** recovery // key :: " + key);
            }
        }
    }

    // 채널로스 장애 처리 함수
    void failureCL(int i, String uid, String sn, String log_date, String ddns_camerausage, String modelNm,
            String firmVer) {
        String fault_code = String.format("%03d", i + 1);
        String key = uid + "||" + sn + "||" + "4" + "||" + fault_code;
        Map<String, String> equipInfo = getEquipmentInfo(sn);

        if (!failureMap.containsKey(key)) {
            Map<String, String> paramMap = commonService.putFailureDataCL(uid, sn, log_date, fault_code, "4",
                    "channelLoss", "1", ddns_camerausage, modelNm, firmVer);
            paramMap.putAll(equipInfo);
            int result = healthDao.insertFailure(paramMap, key);
            if (result == 1) {
                log.info("==> failure  // cmr :: " + ddns_camerausage + " // key :: " + key);
            } else {
                log.error("*** failure // key :: " + key);
            }
        }
    }

    // 채널로스 복구 처리 함수
    void recoveryCL(int i, String uid, String sn, String log_date, String ddns_camerausage) {
        String fault_code = String.format("%03d", i + 1);
        String key = uid + "||" + sn + "||" + "4" + "||" + fault_code;
        if (failureMap.containsKey(key)) {
            Map<String, String> paramMap = commonService.putRecoveryData(failureMap, key);
            int result = healthDao.insertRecovery(paramMap, key);
            if (result == 1) {
                log.info("==> recovery // cmr :: " + ddns_camerausage + " // key :: " + key);
            } else {
                log.error("*** recovery // key :: " + key);
            }
        }
    }

    @Scheduled(cron = "0 0/10 * * * *") // 10분마다 0초에 실행
    // @Scheduled(cron = "0/10 * * * * *") // 테스트 10초에 실행
    public void networkCondition() {
        log.info("==> failureMap.size :: " + failureMap.size());
        log.info("==> focusMap.size :: " + focusMap.size());

        long netOffTime = 10800; // default 3시간
        String allNetYN = "N";
        if (conditionMap.containsKey("allNetOffTime")) {
            allNetYN = "Y";
            netOffTime = Long.parseLong(conditionMap.get("allNetOffTime").get("NETOFF_TIME")) * 60;
        }
        log.info("==> netOffTime = " + allNetYN + " :: " + netOffTime);

        // 패턴과 비교할 현재시간 구하기
        SimpleDateFormat sdf = new SimpleDateFormat("HH:mm:ss");
        Date date = new Date();
        String currTime = sdf.format(date);
        String currHH = currTime.split(":")[0];
        // 오전 시간을 한 자리로 만들기
        if (currHH.startsWith("0")) {
            currHH = currHH.substring(1);
        }

        for (String mac : focusMap.keySet()) {
            JsonObject obj = null;
            try {
                obj = gson.fromJson(focusMap.get(mac), JsonObject.class);
                long log_date = obj.get("log_date").getAsLong();
                String uid = obj.get("ddns_uid").getAsString();
                String sn = obj.get("ddns_mac").getAsString();
                String modelNm = obj.get("ddns_model").getAsString();
                String firmVer = obj.get("ddns_firm").getAsString();
                String industry_code = obj.get("industry_code").getAsString();
                String key = uid + "||" + sn + "||" + "2" + "||" + "001";
                long networkInterval = commonService.getTimeInterval(log_date); // regTime 에서 log_date 로 변경

                Map<String, String> equipInfo = getEquipmentInfo(sn);
                // 패턴 체크
                long setTime;
                if (conditionMap.containsKey("netOff-" + sn)) {
                    setTime = Long.parseLong(conditionMap.get("netOff-" + sn).get("NETOFF_TIME")) * 60;
                } else {
                    setTime = netOffTime;
                }

                // 장애 조건에 맞으면
                if (networkInterval >= setTime && !failureMap.containsKey(key)) {
                    // 네트워크 패턴이 등록돼 있다면
                    if (nvrMaskMap.containsKey("N-" + sn)) {
                        String check_h = nvrMaskMap.get("N-" + sn).get("CHECK_H");
                        String strArr[] = check_h.split("");
                        for (int i = 0; i < strArr.length; i++) {
                            if (i == Integer.parseInt(currHH) && strArr[i].equals("1")) {
                                // 장애발생
                                Map<String, String> paramMap = commonService.putFailureData(uid, sn,
                                        Long.toString(log_date), "001", "2", "networkDisconn", "1", modelNm, firmVer);
                                paramMap.putAll(equipInfo);

                                int result = healthDao.insertFailure(paramMap, key);
                                if (result == 1) {
                                    log.info("==> failure  // net :: " + networkInterval + " // key :: " + key);
                                } else {
                                    log.error("*** failure // key :: " + key);
                                }
                            }
                        }
                    } else if (industryMaskMap.containsKey("N-" + industry_code)) {
                        String check_h = industryMaskMap.get("N-" + industry_code).get("CHECK_H");
                        String strArr[] = check_h.split("");
                        for (int i = 0; i < strArr.length; i++) {
                            if (i == Integer.parseInt(currHH) && strArr[i].equals("1")) {
                                // 장애발생
                                Map<String, String> paramMap = commonService.putFailureData(uid, sn,
                                        Long.toString(log_date), "001", "2", "networkDisconn", "1", modelNm, firmVer);
                                paramMap.putAll(equipInfo);

                                int result = healthDao.insertFailure(paramMap, key);
                                if (result == 1) {
                                    log.info("==> failure  // net :: " + networkInterval + " // key :: " + key);
                                } else {
                                    log.error("*** failure // key :: " + key);
                                }
                            }
                        }
                    } else {
                        Map<String, String> paramMap = commonService.putFailureData(uid, sn, Long.toString(log_date),
                                "001", "2", "networkDisconn", "1", modelNm, firmVer);
                        paramMap.putAll(equipInfo);

                        int result = healthDao.insertFailure(paramMap, key);
                        if (result == 1) {
                            log.info("==> failure  // net :: " + networkInterval + " // key :: " + key);
                        } else {
                            log.error("*** failure // key :: " + key);
                        }
                    }
                }
            } catch (Exception e) {
                log.error(e.toString());
                log.error("******* networkDisconn // obj :: " + obj);
            }
        }
    }
}