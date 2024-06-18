package com.wizontech.adtcaps.entity;

import com.fasterxml.jackson.annotation.JsonProperty;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

@Data
@ApiModel
public class ContractInfoData {

    @JsonProperty("contract_no")
    @ApiModelProperty(value = "계약번호", example = "123456789", required = true)
    private String contract_no;

    @JsonProperty("service_str")
    @ApiModelProperty(value = "서비스 코드", example = "A01/A02/A05/A15/A22/A37", required = true)
    private String service_str;

    @JsonProperty("mon_status")
    @ApiModelProperty(value = "계약 상태", example = "0(경비예정),1(경비중),기타값(헬스분석 대상이 아님)", required = true)
    private String mon_status;

}
