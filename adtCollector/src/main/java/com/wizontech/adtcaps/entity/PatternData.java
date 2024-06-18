package com.wizontech.adtcaps.entity;

import com.fasterxml.jackson.annotation.JsonProperty;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

@Data
@ApiModel
public class PatternData {

    @JsonProperty("PatternSEQ")
    @ApiModelProperty(value = "패턴기준일렬번호", required = true)
    private int PatternSEQ;

    @JsonProperty("Type")
    @ApiModelProperty(value = "패턴 타입", notes = "N(네트워크 단절), R(녹화오류), L(체널로스)", required = true)
    private String Type;

    @JsonProperty("Scope")
    @ApiModelProperty(value = "적용항목", notes = "I(업종), M(녹화기)", required = true)
    private String Scope;

    @JsonProperty("IndustryCode")
    @ApiModelProperty(value = "관제업종코드", required = false)
    private String IndustryCode;

    @JsonProperty("NVRSN")
    @ApiModelProperty(value = "녹화기의 Mac(시리얼)", required = false)
    private String NVRSN;

    @JsonProperty("Category")
    @ApiModelProperty(value = "패턴 적용 여부", notes = "A(자동), C(사용자지정)", required = true)
    private String Category;

    @JsonProperty("Check_H")
    @ApiModelProperty(value = "패턴 시간별 체크", required = true)
    private String Check_H;

    @JsonProperty("Check_L")
    @ApiModelProperty(value = "패턴 채널로스 체크", required = true)
    private String Check_L;

}
