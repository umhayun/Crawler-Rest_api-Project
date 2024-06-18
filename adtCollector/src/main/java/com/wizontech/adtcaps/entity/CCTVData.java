package com.wizontech.adtcaps.entity;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Repository;

@Repository
public class CCTVData {

    public Map<String, String> focusMap;
    public Map<String, String> nsysMap;

    public Map<String, String> tviewStatMap;
    public Map<String, String> tviewConnMap;

    public CCTVData() {
        focusMap = new ConcurrentHashMap<String, String>();
        nsysMap = new ConcurrentHashMap<String, String>();
        // tview
        tviewStatMap = new ConcurrentHashMap<String, String>();
        tviewConnMap = new ConcurrentHashMap<String, String>();

    }

    @Bean
    public Map<String, String> focusMap() {

        return focusMap;
    }

    @Bean
    public Map<String, String> nsysMap() {

        return nsysMap;
    }

    @Bean
    public Map<String, String> tviewStatMap() {

        return tviewStatMap;
    }

    @Bean
    public Map<String, String> tviewConnMap() {

        return tviewConnMap;
    }
}
