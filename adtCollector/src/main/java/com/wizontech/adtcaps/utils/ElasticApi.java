package com.wizontech.adtcaps.utils;

import java.util.Base64;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import org.apache.http.Header;
import org.apache.http.HttpEntity;
import org.apache.http.HttpHost;
import org.apache.http.entity.ContentType;
import org.apache.http.message.BasicHeader;
import org.apache.http.nio.entity.NStringEntity;
import org.apache.http.util.EntityUtils;
import org.elasticsearch.client.Response;
import org.elasticsearch.client.RestClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import com.google.gson.Gson;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Component
public class ElasticApi {

    @Value("${spring.elasticsearch.jest.proxy.host1}")
    private String host;
    @Value("${spring.elasticsearch.jest.proxy.port}")
    private int port;

    @Value("${spring.data.elasticsearch.client.reactive.username}")
    private String username;
    @Value("${spring.data.elasticsearch.client.reactive.password}")
    private String password;

    /**
     * 엘라스틱서치에서 제공하는 api를 이용한 전송메소드
     * 
     * @param method
     * @param url
     * @param obj
     * @param jsonData
     * @return
     */
    public Map<String, Object> callElasticApi(String method, String url, Object jsonData) {
        Map<String, Object> result = new HashMap<>();

        // json형태의 파라미터가 아니라면 gson으로 만들어주자.
        String jsonString = "";

        if (jsonData != null) {
            if (jsonData.getClass().equals(String.class)) {
                jsonString = jsonData.toString();
            } else {
                jsonString = new Gson().toJson(jsonData);
            }
            // log.info("==> jsonString : " + jsonString);
        }

        // String username = "esuser";
        // String password = "qwe123";

        // 엘라스틱서치에서 제공하는 restClient를 통해 엘라스틱서치에 접속한다
        try (RestClient restClient = RestClient.builder(new HttpHost(host, port)).build()) {

            String auth = username + ":" + password;
            String basicAuth = "Basic " + Base64.getEncoder().encodeToString(auth.getBytes());
            Header[] headers = {
                    new BasicHeader("Authorization", basicAuth)
            };
            // log.info("==> 0");
            Map<String, String> params = Collections.singletonMap("pretty", "true");
            // 엘라스틱서치에서 제공하는 response 객체
            Response response = null;
            HttpEntity entity = new NStringEntity(jsonString, ContentType.APPLICATION_JSON);
            // log.info("==> method : " + method);
            // log.info("==> url : " + url);
            // log.info("==> params : " + params.toString());
            // log.info("==> headers : " + headers.toString());

            response = restClient.performRequest(method, url, params, entity, headers);

            if (response == null) {
                log.info("==> response is null!");
            }

            // 앨라스틱서치에서 리턴되는 응답코드를 받는다
            int statusCode = response.getStatusLine().getStatusCode();
            // log.info("==> statusCode : " + statusCode);
            // 엘라스틱서치에서 리턴되는 응답메시지를 받는다
            String responseBody = EntityUtils.toString(response.getEntity());
            // log.info("==> responseBody : " + responseBody);

            result.put("resultCode", statusCode);
            result.put("resultBody", responseBody);

        } catch (Exception e) {
            result.put("resultBody", e.toString());
        }

        return result;
    }
}