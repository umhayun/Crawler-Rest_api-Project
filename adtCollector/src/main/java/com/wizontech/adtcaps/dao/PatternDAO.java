package com.wizontech.adtcaps.dao;

import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Repository;

@Repository
public interface PatternDAO {

    List<Map<String, Object>> getPatternList();

    Map<String, String> getPattern(String patternSeq);

    int insertPattern(Map<String, String> paramMap);

    int updatePattern(Map<String, String> paramMap);

    int deletePattern(String patternSeq);

    void insertIndustryMasking(Map<String, String> paramMap);

    void insertNvrMasking(Map<String, String> paramMap);

    void updateIndustryMasking(Map<String, String> paramMap);

    void updateNvrMasking(Map<String, String> paramMap);

    int deleteIndustryMasking(String patternSeq);

    int deleteNvrMasking(String patternSeq);
}