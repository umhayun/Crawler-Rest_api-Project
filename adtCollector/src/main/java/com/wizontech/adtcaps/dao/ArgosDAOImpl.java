package com.wizontech.adtcaps.dao;

import java.util.Map;

import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

@Repository
public class ArgosDAOImpl implements ArgosDAO {
    @Autowired
    private SqlSessionTemplate sqlSession;

    @Override
    public int updateArgosSendStatus(Map<String, String> argos_status) {
        int result=sqlSession.update("updateArgosStatus", argos_status);
        return result;
    }

    @Override
    public Map<String, String> getArgosSendStatus() {
        return sqlSession.selectOne("getArgosStatus");
    }
    
}
