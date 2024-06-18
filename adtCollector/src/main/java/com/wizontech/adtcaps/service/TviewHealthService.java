package com.wizontech.adtcaps.service;

import java.util.Map;

import javax.annotation.Resource;

import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.stereotype.Service;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.wizontech.adtcaps.dao.CollectDao;
import com.wizontech.adtcaps.dao.HealthDaoImpl;
import com.wizontech.adtcaps.utils.FileUtil;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@EnableScheduling
@Service("TviewHealthService")
public class TviewHealthService implements CollectDao {

  @Autowired
  private FileUtil fileUtil;

  @Resource(name = "failureMap")
  Map<String, Map<String, String>> failureMap;

  @Resource(name = "equipmentInfoMap")
  Map<String, Map<String, String>> equipmentInfoMap;

  @Resource(name = "contractInfoMap")
  Map<String, Map<String, String>> contractInfoMap;

  @Autowired
  private HealthDaoImpl healthDao;

  Gson gson = new Gson();

  @Override
  public void writeJsonToFile(String jsonStr) {
    fileUtil.writeFile("tview_health", jsonStr);
  }

  @Override
  public void failureCondition(JsonObject currObj, JsonObject prevObj) {
  }

  public JsonObject getFaultObj(String mac, String faultType) {
    String key = mac + "||" + mac + "||" + faultType + "||001";

    if (failureMap.containsKey(key)) {
      return gson.fromJson(gson.toJson(failureMap.get(key)), JsonObject.class);
    }

    return null;
  }

  @Override
  public ResponseEntity<String> getData(String bodyData) {
    ResponseEntity<String> BAD_REQUEST = new ResponseEntity<>(HttpStatus.BAD_REQUEST);
    log.info("POST /tviewhealth received");
    HttpStatus status = HttpStatus.INTERNAL_SERVER_ERROR;

    JsonObject jsonObj = null;

    try {
      jsonObj = gson.fromJson(bodyData, JsonObject.class);
    } catch (Exception e) {
      log.error(e.toString());
      log.error("bodyData :: ");
      log.info(bodyData);

      log.info("status :: " + BAD_REQUEST);
      return BAD_REQUEST;
    }

    log.info("=> bodyData: " + jsonObj.toString()); // 서비스 전에 지움

    String macAddress = jsonObj.get("macAddress").getAsString().toUpperCase();
    String connectionStatus = jsonObj.get("connectionStatus").getAsString();
    String sdCardStatus = jsonObj.get("sdCardStatus").getAsString();
    String cameraModel = jsonObj.get("cameraModel").getAsString();

    Map<String, String> equipmentInfo = equipmentInfoMap.get(macAddress);

    String contractNo = "";
    String accountNo = "";
    String serviceStr = "";
    int monStatus = -1;

    if (equipmentInfo != null) {
      contractNo = equipmentInfo.get("contractNo");
      accountNo = equipmentInfo.get("accountNo");
      serviceStr = "";
      Map<String, String> contractInfo = contractInfoMap.get(contractNo);
      if (contractInfo != null) {
        serviceStr = contractInfo.get("serviceStr");
        monStatus = Integer.parseInt(contractInfo.get("monStatus"));
      }
      if ((serviceStr.indexOf("A01") < 0 && serviceStr.indexOf("A02") < 0) || (monStatus != 1 && monStatus != 0)) {
        contractNo = "";
      }
    }

    // D: Cloud 카메라 Network 장애 (connectionStatus 이 CONNECTED가 아닌 경우)
    // E: Cloud 카메라 HDD 장애 (sdCardStatus가 Active가 아닌 경우)
    String signalType = "";
    String faultType = "";
    String faultDesc = "";

    if (!contractNo.equals("")) {
      JsonObject hddFaultObj = getFaultObj(macAddress, "1");
      JsonObject connFaultObj = getFaultObj(macAddress, "2");

      if (hddFaultObj == null && connFaultObj == null) {
        signalType = "E";
      }

      if (signalType.equals("") && hddFaultObj != null && sdCardStatus.equals("Active")) {
        faultType = "1";
        faultDesc = "hddFault";
        signalType = "R";
      }

      if (signalType.equals("") && connFaultObj != null && connectionStatus.equals("CONNECTED")) {
        faultType = "2";
        faultDesc = "networkDisconn";
        signalType = "R";
      }

      if (signalType.equals("")) {
        signalType = "E";
      }

      if (signalType.equals("E") && hddFaultObj == null && !sdCardStatus.equals("Active")) {
        faultType = "1";
        faultDesc = "hddFault";
      }

      if (signalType.equals("E") && connFaultObj == null && !connectionStatus.equals("CONNECTED")) {
        faultType = "2";
        faultDesc = "networkDisconn";
      }

      if (faultType.equals("")) {
        signalType = "P";
      }
    } else {
      signalType = "P";
    }

    Long logDate = System.currentTimeMillis() / 1000;
    LocalDate date = LocalDate.now();
    LocalTime time = LocalTime.now();
    DateTimeFormatter dateFormatter = DateTimeFormatter.ofPattern("yyyyMMdd");
    DateTimeFormatter timeFormatter = DateTimeFormatter.ofPattern("HHmmss");
    String currentDate = date.format(dateFormatter);
    String currentTime = time.format(timeFormatter);

    Map<String, String> paramMap = new HashMap<String, String>();
    paramMap.put("SIGNAL_TYPE", signalType);
    paramMap.put("EQUIPMENT_TYPE", "C");
    paramMap.put("FAULT_TYPE", faultType);
    paramMap.put("FAULT_CODE", "001");
    paramMap.put("FAULT_DESC", faultDesc);
    paramMap.put("ISSUE_DATE", currentDate);
    paramMap.put("ISSUE_TIME", currentTime);
    paramMap.put("SN", macAddress);
    paramMap.put("UID", macAddress);
    paramMap.put("SEND_YN", "N");
    paramMap.put("CAMERA_TYPE", "3");
    paramMap.put("LOG_DATE", Long.toString(logDate));
    paramMap.put("CONTRACT_NO", contractNo);
    paramMap.put("ACCOUNT_NO", accountNo);
    paramMap.put("SERVICE_STR", serviceStr);
    paramMap.put("MODEL_NM", cameraModel);
    paramMap.put("FIRM", "");

    String key = macAddress + "||" + macAddress + "||" + faultType + "||001";

    int insertResult = 0;
    if (signalType.equals("E") && !contractNo.equals("")) {
      insertResult = healthDao.insertFailure(paramMap, key);
    } else if (signalType.equals("R") && !contractNo.equals("")) {
      insertResult = healthDao.insertRecovery(paramMap, key);
    } else if (signalType.equals("P")) {
      insertResult = 1;
    }

    status = insertResult == 1 ? HttpStatus.OK : HttpStatus.INTERNAL_SERVER_ERROR;

    writeJsonToFile(gson.toJson(paramMap, java.util.Map.class));

    log.info("status :: " + status);

    return new ResponseEntity<>(status);
  }
}
