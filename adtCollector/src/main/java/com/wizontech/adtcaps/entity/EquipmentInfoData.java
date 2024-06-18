package com.wizontech.adtcaps.entity;

import com.fasterxml.jackson.annotation.JsonProperty;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

@Data
@ApiModel
public class EquipmentInfoData {

    @JsonProperty("num")
    @ApiModelProperty(value="장비의 고유 키 값", example = "0", required = true)
    private int num;

    @JsonProperty("sn")
    @ApiModelProperty(value = "녹화기의 Mac(시리얼) or UID", example = "0", required = true)
    private String sn;

    @JsonProperty("mac")
    @ApiModelProperty(value = "녹화기의 Mac(시리얼) or UID", example = "0", required = true)
    private String mac;

    @JsonProperty("contract_no")
    @ApiModelProperty(value = "장비 계약번호", example = "0", required = true)
    private String contract_no;
    
    @JsonProperty("account_no")
    @ApiModelProperty(value = "장비 관제번호", example = "0", required = true)
    private String account_no;

}
