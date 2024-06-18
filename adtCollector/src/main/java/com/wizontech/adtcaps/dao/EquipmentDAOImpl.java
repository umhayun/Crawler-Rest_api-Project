package com.wizontech.adtcaps.dao;

import java.util.List;


import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

import com.wizontech.adtcaps.entity.EquipmentData;
import com.wizontech.adtcaps.entity.EquipmentInfoData;


@Repository
public class EquipmentDAOImpl implements EquipmentDAO {

    @Autowired
    private SqlSessionTemplate sqlSession;

    @Override
    public List<EquipmentData> getEquipmentList() {
        List<EquipmentData> resultList = sqlSession.selectList("getEquipmentList");
        return resultList;
    }

    @Override
    public int insertEquipment(EquipmentData equipmentData) {
        int result = sqlSession.insert("insertEquipment", equipmentData);
        return result;
    }

    @Override
    public int updateEquipment(EquipmentData equipmentData) {
        int result = sqlSession.update("updateEquipment", equipmentData);
        return result;
    }

    @Override
    public int deleteEquipment(String NVRSN) {
        int result = sqlSession.delete("deleteEquipment", NVRSN);
        return result;
    }
    
    //EquipmentInfo 
    @Override
    public int insertEquipmentInfo(EquipmentInfoData equipmentInfoData) {
        int result=sqlSession.insert("insertEquipmentInfo", equipmentInfoData);
        return result;
    }

    @Override
    public int updateEquipmentInfo(EquipmentInfoData equipmentInfoData) {
        return sqlSession.update("updateEquipmentInfo", equipmentInfoData);
    }

    @Override
    public int deleteEquipmentInfo(int num) {
        return sqlSession.delete("deleteEquipmentInfo", num);
    }

    @Override
    public EquipmentInfoData getEquipmentInfolist(String sn) {
        EquipmentInfoData equipmentInfoData=sqlSession.selectOne("getEquipmentInfoList", sn);
        return equipmentInfoData;
    }

    @Override
    public EquipmentInfoData getEquipmentInfoNumlist(int num) {
        EquipmentInfoData equipmentInfoData=sqlSession.selectOne("getEquipmentInfoNumList", num);
        return equipmentInfoData;
    }

    

}
