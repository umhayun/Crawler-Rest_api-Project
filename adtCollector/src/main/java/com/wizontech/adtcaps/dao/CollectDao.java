package com.wizontech.adtcaps.dao;

import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import com.google.gson.JsonObject;

@Service
public interface CollectDao {

    void writeJsonToFile(String jsonStr);

    void failureCondition(JsonObject currObj, JsonObject prevObj);

    ResponseEntity<String> getData(String bodyData);

}
