package com.wizontech.adtcaps.dao;

import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Repository;

import com.wizontech.adtcaps.entity.IndustryData;

@Repository
public interface IndustryDAO {

    List<IndustryData> getIndustryList();

    int insertAllIndustry(Map<String, Object> insertMap);

    int updateIndustry(Map<String, String> industryMap);

    int deleteIndustry(String nvr_sn);

    void deleteAllIndustry();
}
