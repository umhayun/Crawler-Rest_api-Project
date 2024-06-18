package com.wizontech.adtcaps.utils;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Component
public class FileUtil {

    @Value("${spring.file.path}")
    private String systemFilePath;

    public void writeFile(String dir, String data) {
        log.debug("==> writeFile" + " // " + "dir : " + dir);
        makeFolder(systemFilePath + "/" + dir);

        String filePath = systemFilePath + "/" + dir + "/" + System.currentTimeMillis() / 1000 + ".json";
        try {
            FileWriter fileWriter = new FileWriter(filePath, true);
            fileWriter.write(data + "\r\n");
            fileWriter.close();

        } catch (IOException e) {
            log.error(e.toString());
        }
    }

    public void makeFolder(String filePath) {
        File dir = new File(filePath);
        if (!dir.exists()) {
            dir.mkdirs();
        }
    }
}
