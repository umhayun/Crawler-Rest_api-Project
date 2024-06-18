package com.wizontech.adtcaps.service;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.stereotype.Service;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.wizontech.adtcaps.dao.CollectDao;
import com.wizontech.adtcaps.utils.FileUtil;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@EnableScheduling
@Service("TviewStatService")
public class TviewStatService implements CollectDao {

    @Autowired
    private FileUtil fileUtil;

    @Autowired
    Map<String, String> tviewStatMap;

    @Override
    public void writeJsonToFile(String jsonStr) {

        fileUtil.writeFile("tview_stat", jsonStr);
    }

    @Override
    public void failureCondition(JsonObject currObj, JsonObject prevObj) {

    }

    @Override
    public ResponseEntity<String> getData(String bodyData) {
        // log.info("==> bodyData :: " + bodyData);
        HttpStatus status = HttpStatus.INTERNAL_SERVER_ERROR;

        Gson gson = new Gson();
        Map<String, String> keyMap = tviewStatMap;

        JsonObject jsonObj = null;
        JsonArray dataArr = null;
        String serverId;
        try {
            jsonObj = gson.fromJson(bodyData, JsonObject.class);
            dataArr = jsonObj.get("data").getAsJsonArray();
            serverId = jsonObj.get("server_id").getAsString();

        } catch (Exception e) {
            status = HttpStatus.BAD_REQUEST;
            log.error(e.toString());
            log.error("******* bodyData :: ");
            log.info(bodyData);

            return new ResponseEntity<>(status);
        }
        log.info("-> dataArrSize :: " + dataArr.size());

        if (dataArr.size() == 0) {
            log.error("******* dataArr is empty");
            log.error("******* bodyData :: ");
            log.error(bodyData);

        } else {
            String key = "";
            JsonObject prevObj = null;
            JsonObject currObj;
            int interval = 0;
            int currObjTime = 0;
            String updateTime = "";

            for (JsonElement dataElement : dataArr) {
                log.info("==> dataElement :: " + dataElement.toString());
                try {
                    long currTime = System.currentTimeMillis() / 1000;
                    currObj = dataElement.getAsJsonObject();
                    currObj.addProperty("log_date", Long.toString(currTime));
                    currObj.addProperty("server_id", serverId);

                    key = currObj.get("mac").getAsString();
                    updateTime = currObj.get("update_time_char").getAsString();
                    // log.info("==> updateTime :: " + updateTime); // 2020.5.12 5:04:00 AM

                    Date date;
                    SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy.MM.dd hh:mm:ss a", Locale.US);
                    try {
                        date = simpleDateFormat.parse(updateTime);
                        // log.info("==> date :: " + date.toString());
                        currObjTime = (int) (date.getTime() / 1000);
                        // 테스트 출력
                        // log.info("==> tviewStat // currObjTime :: " + currObjTime);
                    } catch (Exception e) {
                        log.error(e.toString());
                    }
                    currObj.addProperty("curr_obj_time", currObjTime);

                    // 장애|복구 판단 보류
                    // if (tviewStatMap.containsKey(key)) {
                    // prevObj = gson.fromJson(tviewStatMap.get(key), JsonObject.class);
                    // }
                    // failureCondition(currObj, prevObj);

                    if (prevObj != null) {
                        interval = currObjTime - prevObj.get("curr_obj_time").getAsInt();
                        log.debug(key + " // interval :: " + interval);

                    } else {
                        interval = 0;
                        log.debug(key + " // firstInsert");
                    }
                    currObj.addProperty("data_interval", interval);

                    writeJsonToFile(currObj.toString());
                    keyMap.put(key, currObj.toString());
                    status = HttpStatus.OK;

                } catch (Exception e) {
                    status = HttpStatus.BAD_REQUEST;
                    log.error(e.toString());
                    log.error("****** dataElement :: " + dataElement.toString());
                }
            }
        }
        log.info("-> status :: " + status);

        return new ResponseEntity<>(status);
    }

}
