package com.wizontech.adtcaps.service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.annotation.Resource;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import com.google.gson.Gson;
import com.wizontech.adtcaps.dao.ConditionDAO;
import com.wizontech.adtcaps.entity.ConditionData;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class ConditionService {

    @Resource(name = "conditionMap")
    Map<String, Map<String, String>> conditionMap;

    @Autowired
    private ConditionDAO conditionDAO;

    HttpStatus status = HttpStatus.INTERNAL_SERVER_ERROR;
    Gson gson = new Gson();

    public ResponseEntity<Map<String, Object>> getConditionList() {
        Map<String, Object> resMap = new HashMap<>();
        List<ConditionData> conditionList = conditionDAO.getConditionList();

        if (conditionList.size() > 0) {
            resMap.put("ConditionTotal", conditionList);
            status = HttpStatus.OK;
        } else {
            resMap.put("message", "failure");
            status = HttpStatus.BAD_REQUEST;
            log.error("***** conditionList is empty!");
        }

        return new ResponseEntity<>(resMap, status);
    }

    public ResponseEntity<Map<String, String>> insertCondition(String bodyData) {
        Map<String, String> resMap = new HashMap<>(); // 응답으로 보낼 Map
        Map<String, String> NMap = new HashMap<>(); // conditionMap 에 담을 Map
        Map<String, String> LMap = new HashMap<>(); // conditionMap 에 담을 Map
        Map<String, String> HMap = new HashMap<>(); // conditionMap 에 담을 Map
        Map<String, String> ANMap = new HashMap<>(); // conditionMap 에 담을 Map
        Map<String, String> ALMap = new HashMap<>(); // conditionMap 에 담을 Map
        Map<String, String> AHMap = new HashMap<>(); // conditionMap 에 담을 Map

        resMap.put("message", "failure");
        status = HttpStatus.BAD_REQUEST;

        try {
            ConditionData conditionData = gson.fromJson(bodyData, ConditionData.class);

            if (conditionData.getScope().equals("A")) {
                if (conditionMap.containsKey("allNetOffTime") || conditionMap.containsKey("allLossYN")
                        || conditionMap.containsKey("allHddType")) {
                    log.error("*** duplicated data!");
                } else {
                    int result = conditionDAO.insertCondition(conditionData);
                    if (result == 1) {
                        resMap.put("message", "success");
                        status = HttpStatus.OK;
                        log.info("==> insert success! // TroubleSEQ :: " + conditionData.getTroubleSEQ());

                        if (!conditionData.getNetOff_Time().equals("")) {
                            ANMap.put("TROUBLESEQ", conditionData.getTroubleSEQ());
                            ANMap.put("NETOFF_TIME", conditionData.getNetOff_Time());
                            conditionMap.put("allNetOffTime", ANMap);
                        }
                        if (!conditionData.getLoss_YN().equals("")) {
                            ALMap.put("TROUBLESEQ", conditionData.getTroubleSEQ());
                            ALMap.put("LOSS_YN", conditionData.getLoss_YN());
                            conditionMap.put("allLossYN", ALMap);
                        }
                        if (!conditionData.getHDD_Type().equals("")) {
                            AHMap.put("TROUBLESEQ", conditionData.getTroubleSEQ());
                            AHMap.put("HDD_TYPE", conditionData.getHDD_Type());
                            conditionMap.put("allHddType", AHMap);
                        }
                    } else {
                        log.error("==> insert failure! // TroubleSEQ :: " + conditionData.getTroubleSEQ());
                    }
                }

                // conditionMap test log
                if (conditionMap.containsKey("allNetOffTime")) {
                    log.info("==> allNetOffTime : " + conditionMap.get("allNetOffTime").get("NETOFF_TIME"));
                } else {
                    log.info("==> no allNetOffTime!");
                }
                if (conditionMap.containsKey("allLossYN")) {
                    log.info("==> allLossYN : " + conditionMap.get("allLossYN").get("LOSS_YN"));
                } else {
                    log.info("==> no allLossYN!");
                }
                if (conditionMap.containsKey("allHddType")) {
                    log.info("==> allHddType : " + conditionMap.get("allHddType").get("HDD_TYPE"));
                } else {
                    log.info("==> no allHddType!");
                }
            } else {
                int result = conditionDAO.insertCondition(conditionData);
                if (result == 1) {
                    resMap.put("message", "success");
                    status = HttpStatus.OK;
                    log.info("==> insert success! // TroubleSEQ :: " + conditionData.getTroubleSEQ());

                    if (!conditionData.getNetOff_Time().equals("")) {
                        NMap.put("TROUBLESEQ", conditionData.getTroubleSEQ());
                        NMap.put("NETOFF_TIME", conditionData.getNetOff_Time());
                        conditionMap.put("netOff-" + conditionData.getNVRSN(), NMap);
                    }
                    if (!conditionData.getLoss_YN().equals("")) {
                        LMap.put("TROUBLESEQ", conditionData.getTroubleSEQ());
                        LMap.put("LOSS_YN", conditionData.getLoss_YN());
                        conditionMap.put("loss-" + conditionData.getNVRSN(), LMap);
                    }
                    if (!conditionData.getHDD_Type().equals("")) {
                        HMap.put("TROUBLESEQ", conditionData.getTroubleSEQ());
                        HMap.put("HDD_TYPE", conditionData.getHDD_Type());
                        conditionMap.put("hdd-" + conditionData.getNVRSN(), HMap);
                    }
                } else {
                    log.error("==> insert failure! // TroubleSEQ :: " + conditionData.getTroubleSEQ());
                }
            }
        } catch (Exception e) {
            log.error(e.toString());
            log.error("==> bodyData :: ");
            log.error(bodyData);
        }

        return new ResponseEntity<>(resMap, status);
    }

    public ResponseEntity<Map<String, String>> updateCondition(String bodyData) {
        Map<String, String> resMap = new HashMap<>();
        Map<String, String> LMap = new HashMap<>();
        Map<String, String> NMap = new HashMap<>();
        Map<String, String> HMap = new HashMap<>(); // conditionMap 에 담을 Map
        Map<String, String> ANMap = new HashMap<>(); // conditionMap 에 담을 Map
        Map<String, String> ALMap = new HashMap<>(); // conditionMap 에 담을 Map
        Map<String, String> AHMap = new HashMap<>(); // conditionMap 에 담을 Map

        resMap.put("message", "failure");
        status = HttpStatus.BAD_REQUEST;

        try {
            ConditionData conditionData = gson.fromJson(bodyData, ConditionData.class);
            int result = conditionDAO.updateCondition(conditionData);
            if (result == 1) {
                resMap.put("message", "success");
                status = HttpStatus.OK;
                log.info("==> update success! // TroubleSEQ :: " + conditionData.getTroubleSEQ());

                if (conditionData.getScope().equals("A")) {
                    if (!conditionData.getNetOff_Time().equals("")) {
                        ANMap.put("TROUBLESEQ", conditionData.getTroubleSEQ());
                        ANMap.put("NETOFF_TIME", conditionData.getNetOff_Time());
                        conditionMap.put("allNetOffTime", ANMap);
                    } else {
                        conditionMap.remove("allNetOffTime");
                    }
                    if (!conditionData.getLoss_YN().equals("")) {
                        ALMap.put("TROUBLESEQ", conditionData.getTroubleSEQ());
                        ALMap.put("LOSS_YN", conditionData.getLoss_YN());
                        conditionMap.put("allLossYN", ALMap);
                    } else {
                        conditionMap.remove("allLossYN");
                    }
                    if (!conditionData.getHDD_Type().equals("")) {
                        AHMap.put("TROUBLESEQ", conditionData.getTroubleSEQ());
                        AHMap.put("HDD_TYPE", conditionData.getHDD_Type());
                        conditionMap.put("allHddType", AHMap);
                    } else {
                        conditionMap.remove("allLossYN");
                    }

                    // conditionMap test log
                    if (conditionMap.containsKey("allNetOffTime")) {
                        log.info("==> allNetOffTime : " + conditionMap.get("allNetOffTime").get("NETOFF_TIME"));
                    } else {
                        log.info("==> no allNetOffTime!");
                    }
                    if (conditionMap.containsKey("allLossYN")) {
                        log.info("==> allLossYN : " + conditionMap.get("allLossYN").get("LOSS_YN"));
                    } else {
                        log.info("==> no allLossYN!");
                    }
                    if (conditionMap.containsKey("allHddType")) {
                        log.info("==> allHddType : " + conditionMap.get("allHddType").get("HDD_TYPE"));
                    } else {
                        log.info("==> no allHddType!");
                    }
                } else if (conditionData.getScope().equals("M")) {
                    if (!conditionData.getNetOff_Time().equals("")) {
                        NMap.put("TROUBLESEQ", conditionData.getTroubleSEQ());
                        NMap.put("NETOFF_TIME", conditionData.getNetOff_Time());
                        conditionMap.put("netOff-" + conditionData.getNVRSN(), NMap);
                    }
                    if (!conditionData.getLoss_YN().equals("")) {
                        LMap.put("TROUBLESEQ", conditionData.getTroubleSEQ());
                        LMap.put("LOSS_YN", conditionData.getLoss_YN());
                        conditionMap.put("loss-" + conditionData.getNVRSN(), LMap);
                    }
                    if (!conditionData.getHDD_Type().equals("")) {
                        HMap.put("TROUBLESEQ", conditionData.getTroubleSEQ());
                        HMap.put("HDD_TYPE", conditionData.getHDD_Type());
                        conditionMap.put("hdd-" + conditionData.getNVRSN(), HMap);
                    }
                }
            } else {
                log.error("==> update failure! // TroubleSEQ :: " + conditionData.getTroubleSEQ());
            }
        } catch (Exception e) {
            log.error(e.toString());
            log.error("==> bodyData :: ");
            log.error(bodyData);
        }

        return new ResponseEntity<>(resMap, status);
    }

    public ResponseEntity<Map<String, String>> deleteCondition(String bodyData) {
        Map<String, String> resMap = new HashMap<>();

        resMap.put("message", "failure");
        status = HttpStatus.BAD_REQUEST;

        try {
            ConditionData conditionData = gson.fromJson(bodyData, ConditionData.class);
            String TroubleSEQ = conditionData.getTroubleSEQ();
            int result = conditionDAO.deleteCondition(TroubleSEQ);

            if (result == 1) {
                resMap.put("message", "success");
                status = HttpStatus.OK;
                log.info("==> delete success! // TroubleSEQ :: " + TroubleSEQ);

                for (String key : conditionMap.keySet()) {
                    if (conditionMap.get(key).containsKey("TROUBLESEQ")
                            && conditionMap.get(key).get("TROUBLESEQ").equals(TroubleSEQ)) {
                        conditionMap.remove(key);
                        log.info("==> delete conditionMap // key :: " + key);
                    }
                }
                // log.info("conditionMap: " + conditionMap);
            } else {
                log.error("==> delete failure! // TroubleSEQ :: " + TroubleSEQ);
            }
        } catch (Exception e) {
            log.error(e.toString());
            log.error("==> bodyData :: ");
            log.error(bodyData);
        }

        return new ResponseEntity<Map<String, String>>(resMap, status);
    }
}