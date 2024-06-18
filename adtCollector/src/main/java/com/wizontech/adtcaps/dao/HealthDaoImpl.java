package com.wizontech.adtcaps.dao;

import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import javax.annotation.PostConstruct;
import javax.annotation.Resource;

import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

import com.wizontech.adtcaps.entity.HealthData;
import com.wizontech.adtcaps.entity.HealthInfoData;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Repository
public class HealthDaoImpl implements HealthDao {

    @Resource(name = "failureMap")
    Map<String, Map<String, String>> failureMap;

    @Resource(name = "cLAvgMap")
    Map<String, Map<String, String>> cLAvgMap;

    @Resource(name = "industryMaskMap")
    Map<String, Map<String, String>> industryMaskMap;

    @Resource(name = "nvrMaskMap")
    Map<String, Map<String, String>> nvrMaskMap;

    @Resource(name = "nvrMap")
    Map<String, Map<String, String>> nvrMap;

    @Resource(name = "conditionMap")
    Map<String, Map<String, String>> conditionMap;

    @Resource(name = "equipmentInfoMap")
    Map<String, Map<String, String>> equipmentInfoMap;

    @Resource(name = "contractInfoMap")
    Map<String, Map<String, String>> contractInfoMap;

    @Autowired
    private SqlSessionTemplate sqlSession;

    @PostConstruct
    public void selectFailureList() {
        List<Map<String, String>> failureList = sqlSession.selectList("selectFailureList_current");
        if (failureList.size() > 0) {
            for (Map<String, String> failure : failureList) {
                String key = failure.get("UID") + "||" + failure.get("SN") + "||" + failure.get("FAULT_TYPE") + "||"
                        + failure.get("FAULT_CODE");
                failureMap.put(key, failure);
            }
            log.info("failureMap.size: " + failureMap.size());
        } else {
            log.info("*** No data in failurList ***");
        }
    }

    @PostConstruct
    public void selectCLAvgList() {
        List<Map<String, String>> cLAvgList = sqlSession.selectList("selectCLAvgList");
        if (cLAvgList.size() > 0) {
            for (Map<String, String> cLAvg : cLAvgList) {
                cLAvgMap.put(cLAvg.get("NVRSN"), cLAvg);
            }
            log.info("cLAvgMap.size: " + cLAvgMap.size());
            // log.info("!!! cLAvgMap: " + cLAvgMap);
        } else {
            log.info("*** No data in cLAvgList ***");
        }
    }

    @PostConstruct
    public void selectNvr() {
        List<Map<String, String>> nvrList = sqlSession.selectList("selectNvr");
        if (nvrList.size() > 0) {
            for (Map<String, String> nvr : nvrList) {
                String key = nvr.get("NVRSN");
                nvrMap.put(key, nvr);
            }
            log.info("nvrMap.size: " + nvrMap.size());
        } else {
            log.info("*** No data in nvrList ***");
        }

        // test data!
        // Map<String, String> testMap = new HashMap<>();
        // testMap.put("NVRSN", "1");
        // testMap.put("INDUSTRYCODE", "1111");
        // testMap.put("GROSS", "N");
        // testMap.put("GVIP", "N");
        // testMap.put("DATE_TIME", "2021-08-03 12:15:21");
        // nvrMap.put("1", testMap);
        // log.info("==> nvrMap :: " + nvrMap);
    }

    @PostConstruct
    public void selectIndustyMaskList() {
        List<Map<String, Object>> industryMaskList = sqlSession.selectList("selectIndustyMaskList");
        if (industryMaskList.size() > 0) {
            for (Map<String, Object> industryMask : industryMaskList) {
                Map<String, String> industryMMap = new HashMap<>();
                String key = "N-" + industryMask.get("INDUSTRYCODE");
                industryMMap.put("INDUSTRYCODE", industryMask.get("INDUSTRYCODE").toString());
                industryMMap.put("CATEGORY", industryMask.get("CATEGORY").toString());
                industryMMap.put("CHECK_H", industryMask.get("CHECK_H").toString());
                industryMMap.put("PATTERNSEQ", industryMask.get("PATTERNSEQ").toString());
                industryMaskMap.put(key, industryMMap);
            }
            log.info("industryMaskMap.size: " + industryMaskMap.size());
        } else {
            log.info("*** No data in industryMaskList ***");
        }
    }

    @PostConstruct
    public void selectNvrMaskList() {
        List<Map<String, Object>> nvrMaskList = sqlSession.selectList("selectNvrMaskList");
        if (nvrMaskList.size() > 0) {
            for (Map<String, Object> nvrMask : nvrMaskList) {
                Map<String, String> nvrMMap = new HashMap<>();
                String key = "N-" + nvrMask.get("NVRSN");
                nvrMMap.put("NVRSN", nvrMask.get("NVRSN").toString());
                nvrMMap.put("CATEGORY", nvrMask.get("CATEGORY").toString());
                nvrMMap.put("CHECK_H", nvrMask.get("CHECK_H").toString());
                nvrMMap.put("PATTERNSEQ", nvrMask.get("PATTERNSEQ").toString());
                nvrMaskMap.put(key, nvrMMap);
            }
            log.info("nvrMaskMap.size: " + nvrMaskMap.size());
        } else {
            log.info("*** No data in nvrMaskList ***");
        }
    }

    @PostConstruct
    public void selectConditionList() {
        List<Map<String, String>> conditionList = sqlSession.selectList("selectConditionList");
        String netOffTime = null;
        String lossYN = null;
        String hddType = null;
        if (conditionList.size() > 0) {
            for (Map<String, String> condition : conditionList) {
                Map<String, String> NMap = new HashMap<>();
                Map<String, String> LMap = new HashMap<>();
                Map<String, String> ANMap = new HashMap<>();
                Map<String, String> ALMap = new HashMap<>();
                Map<String, String> AHMap = new HashMap<>();
                if (condition.get("SCOPE").equals("M")) {
                    if (!condition.get("NETOFF_TIME").equals("")) {
                        NMap.put("TROUBLESEQ", condition.get("TROUBLESEQ"));
                        NMap.put("NETOFF_TIME", condition.get("NETOFF_TIME"));
                        conditionMap.put("netOff-" + condition.get("NVRSN"), NMap);
                    }
                    if (!condition.get("LOSS_YN").equals("")) {
                        LMap.put("TROUBLESEQ", condition.get("TROUBLESEQ"));
                        LMap.put("LOSS_YN", condition.get("LOSS_YN"));
                        conditionMap.put("loss-" + condition.get("NVRSN"), LMap);
                    }
                    if (!condition.get("HDD_TYPE").equals("")) {
                        LMap.put("TROUBLESEQ", condition.get("TROUBLESEQ"));
                        LMap.put("HDD_TYPE", condition.get("HDD_TYPE"));
                        conditionMap.put("hdd-" + condition.get("NVRSN"), LMap);
                    }
                }
                if (condition.get("SCOPE").equals("A")) {
                    if (netOffTime == null && !condition.get("NETOFF_TIME").equals("")) {
                        netOffTime = condition.get("NETOFF_TIME");
                        ANMap.put("NETOFF_TIME", netOffTime);
                        conditionMap.put("allNetOffTime", ANMap);
                    }
                    if (lossYN == null && !condition.get("LOSS_YN").equals("")) {
                        lossYN = condition.get("LOSS_YN");
                        ALMap.put("LOSS_YN", lossYN);
                        conditionMap.put("allLossYN", ALMap);
                    }
                    if (hddType == null && !condition.get("HDD_TYPE").equals("")) {
                        hddType = condition.get("HDD_TYPE");
                        AHMap.put("HDD_TYPE", hddType);
                        conditionMap.put("allHddType", AHMap);
                    }
                }
            }
            log.info("conditionMap.size: " + conditionMap.size());
            // log.info("!!! conditionMap: " + conditionMap);
            log.info("allNetOffTime :: " + netOffTime + " // allLossYN :: " + lossYN);
        } else {
            log.info("*** No data in conditionList ***");
        }
    }

    // EquipmentInfo
    @Override
    @PostConstruct
    public void selectEquipmentInfoList() {
        List<Map<String, String>> equipInfoList = sqlSession.selectList("selectEquipmentInfoList");
        if (equipInfoList.size() > 0) {
            for (Map<String, String> equipInfo : equipInfoList) {
                equipmentInfoMap.put(equipInfo.get("sn").toUpperCase(), equipInfo);                
            }
            log.info("equipmentInfoMap.size: " + equipmentInfoMap.size());
        } else {
            log.info("*** No data in equipInfoList ***");
        }

    }

    // ContractInfo
    @Override
    @PostConstruct
    public void selectContractInfoList() {
        List<Map<String, String>> contractInfoList = sqlSession.selectList("selectContractInfoList");
        if (contractInfoList.size() > 0) {
            for (Map<String, String> contInfo : contractInfoList) {
                contractInfoMap.put(contInfo.get("contractNo"), contInfo);
            }
            log.info("ContractInfoMap.size: " + contractInfoMap.size());
        } else {
            log.info("*** No data in ContractInfoMap ***");
        }

    }

    @Override
    public int insertFailure(Map<String, String> paramMap, String key) {
        if (failureMap.get(key) != null) {
            return 0;
        }
        paramMap.put("FULL_DATE", paramMap.get("ISSUE_DATE") + paramMap.get("ISSUE_TIME"));
        String equipmentType = paramMap.get("EQUIPMENT_TYPE");
        String faultType = paramMap.get("FAULT_TYPE");
        String reserved = "";
        if (equipmentType.equals("D")) {
            if (faultType.equals("1")) {
                reserved = "A";
            } else if (faultType.equals("2")) {
                reserved = "C";
            } else if (faultType.equals("4")) {
                reserved = "F";
            }
        } else if (equipmentType.equals("C")) {
            if (faultType.equals("2")) {
                reserved = "D";
            } else if (faultType.equals("1")) {
                reserved = "E";
            }
        }
        paramMap.put("RESERVED", reserved);
        int result = sqlSession.insert("insertFailure", paramMap);
        sqlSession.insert("insertArgosSend", paramMap);
        failureMap.put(key, paramMap);
        return result;
    }

    @Override
    public int insertRecovery(Map<String, String> paramMap, String key) {
        List<Map<String, Object>> failureList = sqlSession.selectList("selectFailure", paramMap);
        int failureSize = failureList.size();
        if (failureList != null && failureSize == 1) {
            int result = sqlSession.insert("insertArgosSend", paramMap);
            sqlSession.delete("deleteFailure", paramMap);
            failureMap.remove(key);
            return result;
        }

        log.error("Select Failure Error. size: " + failureSize + "// key :: " + key);
        return 0;
    }

    @Override
    public List<Map<String, String>> countHealth(HealthData healthData) {

        List<Map<String, String>> rslist = sqlSession.selectList("countHealth", healthData);
        return rslist;
    }

    @Override
    public List<LinkedHashMap<String, Object>> getHealthInfo(HealthInfoData healthInfoData) {
        List<LinkedHashMap<String, Object>> rslist = sqlSession.selectList("getHealthInfo", healthInfoData);
        return rslist;
    }
}
