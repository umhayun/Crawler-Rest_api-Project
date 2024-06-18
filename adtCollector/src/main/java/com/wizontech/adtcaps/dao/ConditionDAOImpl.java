package com.wizontech.adtcaps.dao;

import java.util.List;

import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

import com.wizontech.adtcaps.entity.ConditionData;

@Repository
public class ConditionDAOImpl implements ConditionDAO {

    @Autowired
    private SqlSessionTemplate sqlSession;

    @Override
    public List<ConditionData> getConditionList() {
        List<ConditionData> resultList = sqlSession.selectList("getConditionList");
        return resultList;
    }

    @Override
    public int insertCondition(ConditionData conditionData) {
        int result = sqlSession.insert("insertCondition", conditionData);
        return result;
    }

    @Override
    public int updateCondition(ConditionData conditionData) {
        int result = sqlSession.update("updateCondition", conditionData);
        return result;
    }

    @Override
    public int deleteCondition(String TroubleSEQ) {
        int result = sqlSession.delete("deleteCondition", TroubleSEQ);
        return result;
    }

}
