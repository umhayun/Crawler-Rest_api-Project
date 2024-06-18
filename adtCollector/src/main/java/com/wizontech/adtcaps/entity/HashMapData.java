package com.wizontech.adtcaps.entity;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Repository;

@Repository
public class HashMapData {

    public Map<String, Map<String, String>> failureMap;
    public Map<String, Map<String, String>> nvrMap;
    public Map<String, Map<String, String>> industryMaskMap;
    public Map<String, Map<String, String>> nvrMaskMap;
    public Map<String, Map<String, String>> cLAvgMap;
    public Map<String, Map<String, String>> conditionMap;
    public Map<String, String> cLCountMap;
    public Map<String,  Map<String, String>> equipmentInfoMap;
    public Map<String,  Map<String, String>> contractInfoMap;

    public HashMapData() {
        failureMap = new ConcurrentHashMap<String, Map<String, String>>();
        nvrMap = new ConcurrentHashMap<String, Map<String, String>>();
        industryMaskMap = new ConcurrentHashMap<String, Map<String, String>>();
        nvrMaskMap = new ConcurrentHashMap<String, Map<String, String>>();
        cLAvgMap = new ConcurrentHashMap<String, Map<String, String>>();
        conditionMap = new ConcurrentHashMap<String, Map<String, String>>();
        cLCountMap = new ConcurrentHashMap<String, String>();
        equipmentInfoMap= new ConcurrentHashMap<String, Map<String, String>>();
        contractInfoMap= new ConcurrentHashMap<String, Map<String, String>>();
    }

    @Bean(name = "failureMap")
    public Map<String, Map<String, String>> failureMap() {

        return failureMap;
    }

    @Bean(name = "nvrMap")
    public Map<String, Map<String, String>> nvrMap() {

        return nvrMap;
    }

    @Bean(name = "industryMaskMap")
    public Map<String, Map<String, String>> industryMaskMap() {

        return industryMaskMap;
    }

    @Bean(name = "nvrMaskMap")
    public Map<String, Map<String, String>> nvrMaskMap() {

        return nvrMaskMap;
    }

    @Bean(name = "cLAvgMap")
    public Map<String, Map<String, String>> cLAvgMap() {

        return cLAvgMap;
    }

    @Bean(name = "conditionMap")
    public Map<String, Map<String, String>> conditionMap() {

        return conditionMap;
    }

    @Bean(name = "cLCountMap")
    public Map<String, String> cLCountMap() {

        return cLCountMap;
    }
    @Bean(name="equipmentInfoMap")
    public Map<String, Map<String, String>> equipmentInfoMap(){
        return equipmentInfoMap;
    }

    @Bean(name="contractInfoMap")
    public Map<String, Map<String, String>> contractInfoMap(){
        return contractInfoMap;
    }
}
