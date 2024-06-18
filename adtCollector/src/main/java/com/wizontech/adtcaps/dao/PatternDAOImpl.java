package com.wizontech.adtcaps.dao;

import java.util.List;
import java.util.Map;

import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

@Repository
public class PatternDAOImpl implements PatternDAO {

    @Autowired
    private SqlSessionTemplate sqlSession;

    @Override
    public List<Map<String, Object>> getPatternList() {
        List<Map<String, Object>> resultList = sqlSession.selectList("getPatternList");
        return resultList;
    }

    @Override
    public Map<String, String> getPattern(String patternSeq) {
        Map<String, String> resultMap = sqlSession.selectOne("getPattern", patternSeq);
        return resultMap;
    }

    @Override
    public int insertPattern(Map<String, String> paramMap) {
        int result = sqlSession.insert("insertPattern", paramMap);
        return result;
    }

    @Override
    public int updatePattern(Map<String, String> paramMap) {
        int result = sqlSession.update("updatePattern", paramMap);
        return result;
    }

    @Override
    public int deletePattern(String patternSeq) {
        int result = sqlSession.delete("deletePattern", patternSeq);
        return result;
    }

    @Override
    public void insertIndustryMasking(Map<String, String> paramMap) {
        sqlSession.insert("insertIndustryMasking", paramMap);
    }

    @Override
    public void insertNvrMasking(Map<String, String> paramMap) {
        sqlSession.insert("insertNvrMasking", paramMap);
    }

    @Override
    public void updateIndustryMasking(Map<String, String> paramMap) {
        sqlSession.update("updateIndustryMasking", paramMap);
    }

    @Override
    public void updateNvrMasking(Map<String, String> paramMap) {
        sqlSession.update("updateNvrMasking", paramMap);

    }

    @Override
    public int deleteIndustryMasking(String patternSeq) {
        int result = sqlSession.delete("deleteIndustryMasking", patternSeq);
        return result;
    }

    @Override
    public int deleteNvrMasking(String patternSeq) {
        int result = sqlSession.delete("deleteNvrMasking", patternSeq);
        return result;
    }

}
