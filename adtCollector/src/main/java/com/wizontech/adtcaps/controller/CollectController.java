package com.wizontech.adtcaps.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

import com.wizontech.adtcaps.dao.CollectDao;

@CrossOrigin(origins = "*")
@RequestMapping("/rest/1.0")
@RestController
public class CollectController {

    @Autowired
    @Qualifier("FocusService")
    CollectDao focusService;

    @Autowired
    @Qualifier("NsysService")
    CollectDao nsysService;

    @Autowired
    @Qualifier("TviewStatService")
    CollectDao tviewStatService;

    @Autowired
    @Qualifier("TviewConnService")
    CollectDao tviewConnService;

    @Autowired
    @Qualifier("TviewHealthService")
    CollectDao tviewHealthService;

    @RequestMapping(path = "/focus", method = RequestMethod.POST, produces = "application/json; charset=utf8")
    public ResponseEntity<String> focus(@RequestBody String bodyData) {

        return focusService.getData(bodyData);
    }

    @RequestMapping(path = "/4nsys", method = RequestMethod.POST, produces = "application/json; charset=utf8")
    public ResponseEntity<String> nsys(@RequestBody String bodyData) {

        return nsysService.getData(bodyData);
    }

    @RequestMapping(path = "/*", method = RequestMethod.GET, produces = "application/json; charset=utf8")
    public ResponseEntity<String> getRequest(@RequestBody String bodyData) {
        HttpStatus status = HttpStatus.NOT_FOUND;

        return new ResponseEntity<>(status);
    }

    @RequestMapping(path = "/tviewstat", method = RequestMethod.POST, produces = "application/json; charset=utf8")
    public ResponseEntity<String> tviewStat(@RequestBody String bodyData) {

        return tviewStatService.getData(bodyData);
    }

    @RequestMapping(path = "/tviewconnection", method = RequestMethod.POST, produces = "application/json; charset=utf8")
    public ResponseEntity<String> tviewConn(@RequestBody String bodyData) {

        return tviewConnService.getData(bodyData);
    }

    @RequestMapping(value = "/tviewhealth", method = RequestMethod.POST, produces = "application/json; charset=utf8")
    public ResponseEntity<String> tviewHealth(@RequestBody String bodyData) {
        return tviewHealthService.getData(bodyData);
    }

}