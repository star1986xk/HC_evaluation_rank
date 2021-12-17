#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import datetime
import configparser

cf = configparser.RawConfigParser()
path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'config.ini')
cf.read(path, encoding='utf-8-sig')


def get_settings() -> tuple:
    domain = cf.get('SETTINGS', '域名')
    calculate_date = cf.get('SETTINGS', '计算日期', fallback=datetime.datetime.now().strftime('%Y-%m-%d'))
    run_interval = cf.get('SETTINGS', '启动间隔', fallback=None)
    return domain, calculate_date, run_interval


def get_database() -> tuple:
    database = {
        'host': cf.get('DATABASE', 'HOST'),
        'port': cf.getint('DATABASE', 'PORT'),
        'user': cf.get('DATABASE', 'USER'),
        'password': cf.get('DATABASE', 'PASSWORD'),
        'database': cf.get('DATABASE', 'DATABASE'),
        'charset': 'utf8'
    }
    table = cf.get('DATABASE', 'TABLE')
    return database, table
