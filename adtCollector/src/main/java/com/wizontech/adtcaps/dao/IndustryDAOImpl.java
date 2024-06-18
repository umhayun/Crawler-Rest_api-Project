package com.wizontech.adtcaps.dao;

import java.util.List;
import java.util.Map;

import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

import com.wizontech.adtcaps.entity.IndustryData;

@Repository
public class IndustryDAOImpl implements IndustryDAO {

    @Autowired
    private SqlSessionTemplate sqlSession;

    @Override
    public List<IndustryData> getIndustryList() {
        List<IndustryData> resultList = sqlSession.selectList("getIndustryList");
        return resultList;
    }

    @Override
    public int insertAllIndustry(Map<String, Object> insertMap) {
        int result = sqlSession.insert("insertAllIndustry", insertMap);
        return result;
    }

    @Override
    public int updateIndustry(Map<String, String> industryMap) {
        int result = sqlSession.update("updateIndustry", industryMap);
        return result;
    }

    @Override
    public int deleteIndustry(String nvr_sn) {
        int result = sqlSession.delete("deleteIndustry", nvr_sn);
        return result;
    }

    @Override
    public void deleteAllIndustry() {
        sqlSession.delete("deleteAllIndustry");
    }

}