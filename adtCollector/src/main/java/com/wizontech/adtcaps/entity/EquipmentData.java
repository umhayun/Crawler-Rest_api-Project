package com.wizontech.adtcaps.entity;

import com.fasterxml.jackson.annotation.JsonProperty;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

@Data
@ApiModel
public class EquipmentData {

    @JsonProperty("NVRSN")
    @ApiModelProperty(value = "녹화기의 Mac(시리얼)", example = "0", required = true)
    private String NVRSN;

    @JsonProperty("model")
    @ApiModelProperty(value = "NVR 모델명", example = "0", required = true)
    private String model;

    @JsonProperty("ddns_seq")
    @ApiModelProperty(value = "녹화기 일렬번호", example = "0", required = true)
    private String ddns_seq;

    @JsonProperty("ddns_uid")
    @ApiModelProperty(value = "녹화기 UID", example = "0", required = true)
    private String ddns_uid;

    @JsonProperty("ddns_host_name")
    @ApiModelProperty(value = "녹화기 호스트명", example = "0", required = true)
    private String ddns_host_name;

    @JsonProperty("ddns_serial")
    @ApiModelProperty(value = "녹화기 시리얼", example = "0", required = true)
    private String ddns_serial;

    @JsonProperty("ddns_acc_no")
    @ApiModelProperty(value = "녹화기 계약번호", example = "0", required = true)
    private String ddns_acc_no;

    @JsonProperty("ddns_out_ip")
    @ApiModelProperty(value = "녹화기 접속 아이피(외부아이피)", example = "0", required = true)
    private String ddns_out_ip;

    @JsonProperty("ddns_in_ip")
    @ApiModelProperty(value = "녹회기 내부 아이피", example = "0", required = true)
    private String ddns_in_ip;

    @JsonProperty("ddns_web_port")
    @ApiModelProperty(value = "녹화기 웹포트(원격관리용)", example = "0", required = true)
    private String ddns_web_port;

    @JsonProperty("ddns_net_port")
    @ApiModelProperty(value = "녹화기 영상포트(영상전송용)", example = "0", required = true)
    private String ddns_net_port;

    @JsonProperty("ddns_hdd")
    @ApiModelProperty(value = "HDD 상태값", example = "0", required = true)
    private String ddns_hdd;

    @JsonProperty("ddns_ch")
    @ApiModelProperty(value = "카메라 상태값", example = "0", required = true)
    private String ddns_ch;

    @JsonProperty("ddns_firm")
    @ApiModelProperty(value = "녹화기 펌웨어 버전", example = "0", required = true)
    private String ddns_firm;

    @JsonProperty("ddns_dvr_date")
    @ApiModelProperty(value = "녹화기의 날짜", example = "0", required = true)
    private String ddns_dvr_date;

    @JsonProperty("ddns_dvr_time")
    @ApiModelProperty(value = "녹화기의 시간", example = "0", required = true)
    private String ddns_dvr_time;

    @JsonProperty("ddns_server_date")
    @ApiModelProperty(value = "전송시 서버의 날짜", example = "0", required = true)
    private String ddns_server_date;

    @JsonProperty("ddns_server_time")
    @ApiModelProperty(value = "전송시 서버의 시간", example = "0", required = true)
    private String ddns_server_time;

    @JsonProperty("hdd")
    @ApiModelProperty(value = "hdd", notes = "0: No HDD, 1: Disk error, 2: 정상", example = "0", required = true)
    private String hdd;

    @JsonProperty("firm")
    @ApiModelProperty(value = "firm", notes = "NVR F/W Version", example = "0", required = true)
    private String firm;

    @JsonProperty("camer_usage")
    @ApiModelProperty(value = "camer_usage", notes = "0: No use, 1: 정상, 2: 사용안함 채널 영상없음, 3: 사용함 채널 영상없음", example = "0", required = true)
    private String camer_usage;

    @JsonProperty("rec_start_time_char")
    @ApiModelProperty(value = "녹화 시작시간", example = "0", required = true)
    private String rec_start_time_char;

    @JsonProperty("rec_end_time_char")
    @ApiModelProperty(value = "녹화 시작시간", notes = "A(전체), G(Gross), V(GVIP), I(업종), M(녹화기)", example = "0", required = true)
    private String rec_end_time_char;

    @JsonProperty("update_time_char")
    @ApiModelProperty(value = "마지막 녹화시간", example = "0", required = true)
    private String update_time_char;

    @JsonProperty("safeBackupCameras")
    @ApiModelProperty(value = "안심백업 채널 설정 정보", notes = "추후 필요 시 정보 활용 예정", example = "0", required = true)
    private String safeBackupCameras;

    @JsonProperty("rtsp_connection")
    @ApiModelProperty(value = "rtsp_connection", notes = "0: NVR rtsp 연결상태 단절, 1: 정상", example = "0", required = true)
    private String rtsp_connection;

    @JsonProperty("mq_conncetion")
    @ApiModelProperty(value = "mq_conncetion", notes = "0: NVR mqtt 연결상태 단절, 1: 정상", example = "0", required = true)
    private String mq_conncetion;

    @JsonProperty("Status")
    @ApiModelProperty(value = "장애상태값", notes = "(T)장애, (E)복구, 사용가능", example = "0", required = true)
    private String Status;
}
