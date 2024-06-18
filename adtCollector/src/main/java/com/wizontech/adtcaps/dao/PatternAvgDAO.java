package com.wizontech.adtcaps.dao;

import java.util.Map;

public interface PatternAvgDAO {
    Map<String, Object> getResultMap(String category, String key, String value);
}
