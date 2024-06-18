package com.wizontech.adtcaps.entity;

import com.fasterxml.jackson.annotation.JsonProperty;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

@Data
@ApiModel
public class ConditionData {

    @JsonProperty("TroubleSEQ")
    @ApiModelProperty(value = "장애기준일렬번호", required = true)
    private String TroubleSEQ;

    @JsonProperty("Scope")
    @ApiModelProperty(value = "적용항목", notes = "A(전체), G(Gross), V(GVIP), I(업종), M(녹화기)", required = true)
    private String Scope;

    @JsonProperty("IndustryCode")
    @ApiModelProperty(value = "관제업종코드", notes = "적용항목이 업종일경우 필수")
    private String IndustryCode;

    @JsonProperty("NVRSN")
    @ApiModelProperty(value = "녹화기 Mac(시리얼)", notes = "적용항목이 Gross, GVIP, 녹화기일경우 필수")
    private String NVRSN;

    @JsonProperty("NetOff_Time")
    @ApiModelProperty(value = "네트워크단절", notes = "네트워크단절(분)", example = "180")
    private String NetOff_Time;

    @JsonProperty("UpdateTime_RecEnd_Time")
    @ApiModelProperty(value = "녹화장애(NVR Info 생성시간와 마지막 녹화시간 비교)", notes = "녹화장애구분이 R 일 경우 필수", example = "60")
    private String UpdateTime_RecEnd_Time;

    @JsonProperty("RecstartTime_RecEnd_Time")
    @ApiModelProperty(value = "녹화장애(녹화 시작시간과 마지막녹화시간 비교)", notes = "녹화장애구분이 R 일 경우 필수", example = "720")
    private String RecstartTime_RecEnd_Time;

    @JsonProperty("Loss_YN")
    @ApiModelProperty(value = "채널 Loss 장애 구분", notes = "Y(패턴적용), N(페턴적용안함)", required = true)
    private String Loss_YN;

    @JsonProperty("HDD_Type")
    @ApiModelProperty(value = "HDD 장애 구분", notes = "Y(장애처리사용), N(장애처리안함)", example = "Y", required = true)
    private String HDD_Type;

    @JsonProperty("Date_Time")
    @ApiModelProperty(value = "적용일시", hidden = true)
    private String Date_Time;

}