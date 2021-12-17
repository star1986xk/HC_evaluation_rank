#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
主py    初始化日志对象：
from utils.my_log import init_log
logger = init_log('my')

其他py  直接引用日志对象:
logger = logging.getLogger('my')
"""
import os
import sys
import logging
import logging.handlers


def init_log(filename):
    logger = logging.getLogger(filename)
    logger.setLevel(logging.INFO)
    file_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(file_dir, filename)
    # 每 1(interval) 天(when) 重写1个文件,保留7(backupCount) 个旧文件；when还可以是Y/m/H/M/S
    fh = logging.handlers.TimedRotatingFileHandler(file_path + '.log', when='d', interval=1, backupCount=3,
                                                   encoding='utf-8')
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(lineno)d - %(funcName)s - %(process)d - %(processName)s - %(message)s',
        '%Y/%m/%d %H:%M:%S %p')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger
