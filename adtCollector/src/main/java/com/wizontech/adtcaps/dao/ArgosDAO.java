package com.wizontech.adtcaps.dao;

import java.util.Map;

import org.springframework.stereotype.Service;

@Service
public interface ArgosDAO {

    int updateArgosSendStatus(Map<String,String> argos_status);

    Map<String,String> getArgosSendStatus();

}
