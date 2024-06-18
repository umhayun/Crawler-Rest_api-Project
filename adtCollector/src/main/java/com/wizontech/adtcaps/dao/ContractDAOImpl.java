package com.wizontech.adtcaps.dao;


import java.util.Map;

import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Repository;

import com.wizontech.adtcaps.entity.ContractInfoData;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@EnableScheduling
@Repository
public class ContractDAOImpl implements ContractDAO{
    @Autowired
    private SqlSessionTemplate sqlSession;
    
    @Override
    public int updateContractInfo(ContractInfoData contractInfoData) {
        int result=sqlSession.insert("InsertContractInfo", contractInfoData);
        return result;
    }

    @Override
    public Map<String,String> getContractInfo(String conNo) { 
        Map<String,String> result=sqlSession.selectOne("getContractInfoList", conNo);
        return result;
    }
    
    @Scheduled(cron="0 0 2 * * *")
    @Override
    public void deleteContractInfo() {        
        int result=sqlSession.delete("deleteContractInfo");
        if (result>0){
            log.info("CONTRACTINFO DELETE SUCCESS : "+result);
        }
        else{
            log.info("CONTRACTINFO DELETE FAILURE : "+result);
        }
       
    }

    

    
}
