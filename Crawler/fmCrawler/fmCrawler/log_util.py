# -*- coding: utf-8 -*-


import configparser
import logging
import logging.handlers

from datetime import datetime 
from scrapy.utils.project import get_project_settings


class LogUtil:
    level = 'DEBUG'
    
    def __init__(self, logger_name): 

        self.settings = get_project_settings()

        self.logger = logging.getLogger(logger_name)
        
        if self.logger.level == 0: 
            formatter = logging.Formatter('%(asctime)s (%(filename)s:%(lineno)s) [%(levelname)s] %(message)s')
            
            # log를 파일에 출력, 10MB 파일을 50개까지 남김 
            file_handler = logging.handlers.RotatingFileHandler(self.settings['LOG_PATH'] + logger_name + '_{:%Y%m%d}.log'.format(datetime.now()), 
                    maxBytes = 1024*1024*10, backupCount = 50, encoding = 'utf-8')
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            
            if self.level == 'DEBUG':
                #DEBUG 모드에서는 console로도 log를 남김 
                streamHandler = logging.StreamHandler()
                streamHandler.setFormatter(formatter)
                self.logger.addHandler(streamHandler)
                self.logger.setLevel(logging.DEBUG)
                self.logger.debug('current logging level is DEBUG')
            elif self.level == 'INFO':
                self.logger.setLevel(logging.INFO)
                self.logger.debug('current logging level is INFO')
            elif self.level == 'ERROR':
                self.logger.setLevel(logging.ERROR)
                self.logger.debug('current logging level is ERROR')
            else:
                self.logger.setLevel(logging.ERROR)
                self.logger.debug('current logging level is not set (default: ERROR)')

    def get_logger(self): 
        return self.logger
