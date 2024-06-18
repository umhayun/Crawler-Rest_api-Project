package com.wizontech.adtcaps.service;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Map;
import java.util.HashMap;

import javax.annotation.Resource;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import com.wizontech.adtcaps.dao.CollectDao;
import com.wizontech.adtcaps.dao.HealthDaoImpl;
import com.wizontech.adtcaps.utils.FileUtil;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service("NsysService")
public class NsysService implements CollectDao {

    @Autowired
    private FileUtil fileUtil;

    @Autowired
    Map<String, String> nsysMap;

    @Autowired
    private CommonService commonService;

    @Autowired
    private HealthDaoImpl healthDao;

    @Resource(name = "failureMap")
    Map<String, Map<String, String>> failureMap;

    @Resource(name = "conditionMap")
    Map<String, Map<String, String>> conditionMap;

    @Resource(name = "nvrMap")
    Map<String, Map<String, String>> nvrMap;

    @Resource(name = "industryMaskMap")
    Map<String, Map<String, String>> industryMaskMap;

    @Resource(name = "nvrMaskMap")
    Map<String, Map<String, String>> nvrMaskMap;

    @Resource(name = "equipmentInfoMap")
    Map<String, Map<String, String>> equipmentInfoMap;

    @Resource(name = "contractInfoMap")
    Map<String, Map<String, String>> contractInfoMap;

    @Override
    public void writeJsonToFile(String jsonStr) {

        fileUtil.writeFile("4nsys", jsonStr);
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

        if ((serviceStr.indexOf("A01") < 0 && serviceStr.indexOf("A02") < 0) || (monStatus != 1 && monStatus != 0)) {
            return null;
        }

        Map<String, String> paramMap = new HashMap<String, String>();
        paramMap.put("CONTRACT_NO", contractNo);
        paramMap.put("ACCOUNT_NO", accountNo);
        paramMap.put("SERVICE_STR", serviceStr);

        return paramMap;
    }

    public String getFirmVersion(JsonObject obj) {
        String firmVer = "";

        for (int i = 1; i < 5; i++) {
            firmVer += obj.get("ver_fw_ver_" + i).getAsString();
            if (i < 4) {
                firmVer += ".";
            }
        }
        return firmVer;
    }

    @Override
    public ResponseEntity<String> getData(String bodyData) {
        log.info("POST /4nsys received");
        int resultCount = 0;
        HttpStatus status = HttpStatus.INTERNAL_SERVER_ERROR;

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
                    currTime = System.currentTimeMillis() / 1000; // log_date
                    currTimstamp = sdf.format(currTime * 1000); // log_timestamp

                    currObj.addProperty("log_date", Long.toString(currTime));
                    currObj.addProperty("log_timestamp", currTimstamp);
                    currObj.addProperty("server_id", serverId);

                    // nvrMap에 키가 있으면 데이터 가져와서 add, 없으면 공백 넣기
                    mac = currObj.get("did").getAsString().toUpperCase();
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
                    key = currObj.get("nif_uid").getAsString().toUpperCase() + "||" + mac;
                    if (nsysMap.containsKey(key)) {
                        prevObj = gson.fromJson(nsysMap.get(key), JsonObject.class);
                    }
                    failureCondition(currObj, prevObj);
                    if (prevObj != null) {
                        prevTime = prevObj.get("log_date").getAsLong();
                        interval = currTime - prevTime;
                        log.debug(key + " // interval :: " + interval);
                        if (interval < 0) {
                            log.info("interval :: " + currTime + " - " + prevTime + " = " + interval + " // key :: "
                                    + key);
                        }
                    } else {
                        log.debug(key + " // firstInsert");
                    }
                    currObj.addProperty("data_interval", interval);

                    writeJsonToFile(currObj.toString());
                    nsysMap.put(key, currObj.toString());
                    status = HttpStatus.OK;
                    resultCount += 1;
                } catch (Exception e) {
                    status = HttpStatus.BAD_REQUEST;
                    log.error(e.toString());
                    log.error("*** dataElement :: " + dataElement.toString());
                }
            }
        }
        log.info("status :: " + status + " // Result Count: " + resultCount);

        return new ResponseEntity<>(status);
    }

    @Override
    public void failureCondition(JsonObject currObj, JsonObject prevObj) {
        String uid = currObj.get("nif_uid").getAsString().toUpperCase();
        String sn = currObj.get("did").getAsString().toUpperCase();
        String log_date = currObj.get("log_date").getAsString();
        String modelNm = currObj.get("model").getAsString();
        String firmVer = getFirmVersion(currObj);
        String key;

        long up_time = Long.parseLong(currObj.get("up_time").getAsString());
        long hif_rec_end_time = Long.parseLong(currObj.get("hif_rec_end_time").getAsString());
        long currentTime = System.currentTimeMillis() / 1000;
        long timeDiff1 = Math.abs(up_time - hif_rec_end_time);
        long timeDiff2 = Math.abs(currentTime - hif_rec_end_time);

        Map<String, String> equipInfo = getEquipmentInfo(sn);
        if (equipInfo == null) {
            return;
        }
        // HDD오류(1)
        key = uid + "||" + sn + "||" + "1" + "||" + "001";
        int hif_hdd_error = currObj.get("hif_hdd_error").getAsInt();

        String allHddType = "Y";
        if (conditionMap.containsKey("allHddType")) {
            allHddType = conditionMap.get("allHddType").get("HDD_TYPE");
        }
        if (conditionMap.containsKey("hdd-" + sn)) {
            if (!conditionMap.get("hdd-" + sn).get("HDD_TYPE").equals("N")) {
                // 장애 판단
                if (timeDiff1 >= 3600 && hif_hdd_error != 0 && timeDiff2 >= 172800 && !failureMap.containsKey(key)) { // 3600:60m,
                                                                                                                      // 172800:48h
                    Map<String, String> paramMap = commonService.putFailureData(uid, sn, log_date, "001", "1",
                            "hddFault", "2", modelNm, firmVer);
                    paramMap.putAll(equipInfo);
                    int result = healthDao.insertFailure(paramMap, key);
                    if (result == 1) {
                        log.info("==> failure  // hdd :: " + hif_hdd_error + " // key :: " + key);
                    } else {
                        log.error("*** failure // key :: " + key);
                    }
                } else if (timeDiff1 < 3600 || hif_hdd_error == 0 || timeDiff2 < 172800
                        && failureMap.containsKey(key)) { // 3600:60m, 172800:48h
                    Map<String, String> paramMap = commonService.putRecoveryData(failureMap, key);
                    int result = healthDao.insertRecovery(paramMap, key);
                    if (result == 1) {
                        log.info("==> recovery // hdd :: " + hif_hdd_error + " // key :: " + key);
                    } else {
                        log.error("*** recovery // key :: " + key);
                    }
                }
            }
        } else {
            if (allHddType.equals("Y")) {
                // 장애 판단
                if ((timeDiff1 >= 3600 && hif_hdd_error != 0 && timeDiff2 >= 172800) && !failureMap.containsKey(key)) { // 3600:60m,
                                                                                                                        // 172800:48h
                    Map<String, String> paramMap = commonService.putFailureData(uid, sn, log_date, "001", "1",
                            "hddFault", "2", modelNm, firmVer);
                    paramMap.putAll(equipInfo);
                    int result = healthDao.insertFailure(paramMap, key);
                    if (result == 1) {
                        log.info("==> failure  // hdd :: " + hif_hdd_error + " // key :: " + key);
                    } else {
                        log.error("*** failure // key :: " + key);
                    }
                } else if ((timeDiff1 < 3600 || hif_hdd_error == 0 || timeDiff2 < 172800)
                        && failureMap.containsKey(key)) { // 3600:60m, 172800:48h
                    Map<String, String> paramMap = commonService.putRecoveryData(failureMap, key);
                    int result = healthDao.insertRecovery(paramMap, key);
                    if (result == 1) {
                        log.info("==> recovery // hdd :: " + hif_hdd_error + " // key :: " + key);
                    } else {
                        log.error("*** recovery // key :: " + key);
                    }
                }
            }
        }

        // 네트워크 단선 복구 조건
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

    @Scheduled(cron = "0 0/10 * * * *")
    // @Scheduled(cron = "0/10 * * * * *") // 10초에 실행
    public void networkCondition() {
        log.info("==> nsysMap.size :: " + nsysMap.size());

        Map<String, String> paramMap;

        JsonObject obj = null;
        long log_date;
        String uid;
        String sn;
        String industry_code;
        String key;
        String currTime;
        String currHH;
        String modelNm;
        String firmVer;
        long networkInterval;
        int result;
        String check_h;
        String strArr[];
        long netOffTime = 10800; // default 3시간
        long setTime;

        String allNetYN = "N";
        if (conditionMap.containsKey("allNetOffTime")) {
            allNetYN = "Y";
            netOffTime = Long.parseLong(conditionMap.get("allNetOffTime").get("NETOFF_TIME")) * 60;
        }
        log.info("==> netOffTime = " + allNetYN + " :: " + netOffTime);

        // 패턴과 비교할 현재시간 구하기
        SimpleDateFormat sdf = new SimpleDateFormat("HH:mm:ss");
        Date date = new Date();
        currTime = sdf.format(date);
        currHH = currTime.split(":")[0];
        // 오전 시간을 한 자리로 만들기
        if (currHH.startsWith("0")) {
            currHH = currHH.substring(1);
        }

        for (String mapKey : nsysMap.keySet()) {
            try {
                obj = gson.fromJson(nsysMap.get(mapKey), JsonObject.class);

                log_date = obj.get("log_date").getAsLong();
                uid = obj.get("nif_uid").getAsString().toUpperCase();
                sn = obj.get("did").getAsString().toUpperCase();
                industry_code = obj.get("industry_code").getAsString(); // ""
                modelNm = obj.get("model").getAsString();
                firmVer = getFirmVersion(obj);

                Map<String, String> equipInfo = getEquipmentInfo(sn);

                // 패턴 체크
                if (conditionMap.containsKey("netOff-" + sn)) {
                    setTime = Long.parseLong(conditionMap.get("netOff-" + sn).get("NETOFF_TIME")) * 60;
                } else {
                    setTime = netOffTime;
                }

                networkInterval = commonService.getTimeInterval(log_date); // up_time 에서 log_date 로 변경
                key = uid + "||" + sn + "||" + "2" + "||" + "001";
                // 장애 조건에 맞으면
                if (networkInterval >= setTime && !failureMap.containsKey(key)) { // 10800: 3시간
                    // 네트워크 패턴이 등록돼 있다면
                    if (nvrMaskMap.containsKey("N-" + sn)) {
                        check_h = nvrMaskMap.get("N-" + sn).get("CHECK_H");
                        strArr = check_h.split("");
                        for (int i = 0; i < strArr.length; i++) {
                            if (i == Integer.parseInt(currHH) && strArr[i].equals("1")) {
                                // 장애발생
                                paramMap = commonService.putFailureData(uid, sn, Long.toString(log_date), "001", "2",
                                        "networkDisconn", "2", modelNm, firmVer);
                                paramMap.putAll(equipInfo);
                                result = healthDao.insertFailure(paramMap, key);
                                if (result == 1) {
                                    log.info("==> failure  // net :: " + networkInterval + " // key :: " + key);
                                } else {
                                    log.error("*** failure // key :: " + key);
                                }
                            }
                        }
                    } else if (industryMaskMap.containsKey("N-" + industry_code)) {
                        check_h = industryMaskMap.get("N-" + industry_code).get("CHECK_H");
                        strArr = check_h.split("");
                        for (int i = 0; i < strArr.length; i++) {
                            if (i == Integer.parseInt(currHH) && strArr[i].equals("1")) {
                                // 장애발생
                                paramMap = commonService.putFailureData(uid, sn, Long.toString(log_date), "001", "2",
                                        "networkDisconn", "2", modelNm, firmVer);
                                paramMap.putAll(equipInfo);
                                result = healthDao.insertFailure(paramMap, key);
                                if (result == 1) {
                                    log.info("==> failure  // net :: " + networkInterval + " // key :: " + key);
                                } else {
                                    log.error("*** failure // key :: " + key);
                                }
                            }
                        }
                    } else {
                        paramMap = commonService.putFailureData(uid, sn, Long.toString(log_date), "001", "2",
                                "networkDisconn", "2", modelNm, firmVer);
                        paramMap.putAll(equipInfo);
                        result = healthDao.insertFailure(paramMap, key);
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