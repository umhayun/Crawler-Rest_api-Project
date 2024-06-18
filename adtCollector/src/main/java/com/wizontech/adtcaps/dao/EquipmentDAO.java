package com.wizontech.adtcaps.dao;

import java.util.List;

import com.wizontech.adtcaps.entity.EquipmentData;
import com.wizontech.adtcaps.entity.EquipmentInfoData;

public interface EquipmentDAO {

    List<EquipmentData> getEquipmentList();

    int insertEquipment(EquipmentData equipmentData);

    int updateEquipment(EquipmentData equipmentData);

    int deleteEquipment(String NVRSN);

    int insertEquipmentInfo(EquipmentInfoData equipmentInfoData);

    int updateEquipmentInfo(EquipmentInfoData equipmentInfoData);

    int deleteEquipmentInfo(int num);

    EquipmentInfoData getEquipmentInfolist(String sn);

    EquipmentInfoData getEquipmentInfoNumlist(int num);


}