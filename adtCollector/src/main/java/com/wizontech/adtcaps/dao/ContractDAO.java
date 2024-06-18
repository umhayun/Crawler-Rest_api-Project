package com.wizontech.adtcaps.dao;


import java.util.Map;

import com.wizontech.adtcaps.entity.ContractInfoData;

public interface ContractDAO {

    int updateContractInfo(ContractInfoData contractInfoData);
    Map<String,String> getContractInfo(String conNo);
    void deleteContractInfo();
}
