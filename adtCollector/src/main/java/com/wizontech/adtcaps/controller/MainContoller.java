package com.wizontech.adtcaps.controller;

import java.net.InetAddress;

import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.view.RedirectView;

@CrossOrigin(origins = "*")
@RestController
public class MainContoller {

    @RequestMapping(path = "/", method = RequestMethod.GET)
    public RedirectView main() {

        return new RedirectView("/swagger-ui.html");
    }

    @RequestMapping(path = "/ip", method = RequestMethod.GET)
    public String getIp() {
        String host = "";
        try {
            host = InetAddress.getLocalHost().getHostAddress();
        } catch (Exception e) {
            e.printStackTrace();
        }

        return "connected :: " + host;
    }
}