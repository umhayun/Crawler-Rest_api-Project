package com.wizontech.adtcaps.entity;

import com.fasterxml.jackson.annotation.JsonProperty;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

@Data
@ApiModel
public class IndustryData {

    @JsonProperty("NVRSN")
    @ApiModelProperty(value = "녹화기 Mac(시리얼)", required = true)
    private String NVRSN;

    @JsonProperty("IndustryCode")
    @ApiModelProperty(value = "관제업종코드", required = true)
    private String IndustryCode;

    @JsonProperty("Gross")
    @ApiModelProperty(value = "Gross", example = "N", required = true)
    private String Gross;

    @JsonProperty("GVIP")
    @ApiModelProperty(value = "GVIP", example = "N", required = true)
    private String GVIP;

    @JsonProperty("DATE_TIME")
    @ApiModelProperty(value = "GVIP", hidden = true)
    private String DATE_TIME;

}
