package com.wizontech.adtcaps.dao;

import java.util.List;

import com.wizontech.adtcaps.entity.ConditionData;

public interface ConditionDAO {

    List<ConditionData> getConditionList();

    int insertCondition(ConditionData conditionData);

    int updateCondition(ConditionData conditionData);

    int deleteCondition(String TroubleSEQ);

}