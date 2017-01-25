#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging 
from logging.handlers import TimedRotatingFileHandler 

log = logging.getLogger()


def set_logger(level='INFO', logpath='default'):
    log_formatter = logging.Formatter('%(asctime)s [%(funcName)s: %(filename)s,%(lineno)d] %(levelname)s: %(message)s')
    log_handler = TimedRotatingFileHandler(logpath, when="midnight", backupCount=7) 
    log_handler.suffix = "%Y%m%d"
    log_handler.setFormatter(log_formatter) 
    log.addHandler(log_handler)
    if level == 'INFO':
        log.setLevel(logging.INFO)
    elif level == 'WARNING':
        log.setLevel(logging.WARNING)
    elif level == 'DEBUG':
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
