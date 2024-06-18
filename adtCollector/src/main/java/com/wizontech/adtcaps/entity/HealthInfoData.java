package com.wizontech.adtcaps.entity;

import com.fasterxml.jackson.annotation.JsonProperty;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

@Data
@ApiModel
public class HealthInfoData {

    @JsonProperty("Total_Count")
    @ApiModelProperty(value = "장애리스트 카운트", example = "123456789", required = true)
    private int Total_Count;

    @JsonProperty("List_Start_Num")
    @ApiModelProperty(value = "리스트 시작 no", example = "123456789", required = true)
    private int List_Start_Num;

    @JsonProperty("List_End_Num")
    @ApiModelProperty(value = "리스트 마지막 no", example = "123456789", required = true)
    private int List_End_Num;

    @JsonProperty("HARTL_Issuse_Date_Start")
    @ApiModelProperty(value = "리스트 마지막 no", example = "123456789", required = true)
    private String HARTL_Issuse_Date_Start;

    @JsonProperty("HARTL_Issuse_Date_End")
    @ApiModelProperty(value = "리스트 마지막 no", example = "123456789", required = true)
    private String HARTL_Issuse_Date_End;

    @JsonProperty("HARTL_Fault_Type")
    @ApiModelProperty(value = "장애유형", example = "1(HDD 장애), 2(Network 단절), 4(채널로스 장애) ''(없으면 전체 검색)", required = true)
    private String HARTL_Fault_Type;

    @JsonProperty("sn")
    @ApiModelProperty(value = "녹화기 sn", example = "123456789", required = true)
    private String sn;

    @JsonProperty("contractNo")
    @ApiModelProperty(value = "계약번호", example = "123456789", required = true)
    private String contractNo;

    @JsonProperty("accountNo")
    @ApiModelProperty(value = "관제번호", example = "123456789", required = true)
    private String accountNo;

    
    @JsonProperty("HARTL_Nomodify")
    @ApiModelProperty(value = "장애 미복구", example = "값이 없으면 검색 조건 적용 x", required = true)
    private String HARTL_Nomodify;



}
