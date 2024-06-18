package com.wizontech.adtcaps.dao;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Repository;

import com.wizontech.adtcaps.entity.HealthData;
import com.wizontech.adtcaps.entity.HealthInfoData;

@Repository
public interface HealthDao {

    public void selectFailureList();

    public void selectCLAvgList();

    public void selectNvr();

    public void selectIndustyMaskList();

    public void selectNvrMaskList();

    public void selectConditionList();

    public void selectEquipmentInfoList();

    public void selectContractInfoList();

    public int insertFailure(Map<String, String> paramMap, String key);

    public int insertRecovery(Map<String, String> paramMap, String key);

    public List<Map<String,String>> countHealth(HealthData healthData);

    public List<LinkedHashMap<String,Object>> getHealthInfo(HealthInfoData healthInfoData);

}