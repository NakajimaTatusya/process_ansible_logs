#!/usr/bin/python3
# coding:utf-8

"""
ANsible log ファイルを読み込んでフォーマットする
"""

import configparser
import glob
import os
import json
import pprint
import re

from logging.config import dictConfig
from logging import getLogger

from datetime import datetime as DT
from library import Utilities

# ログレベル定義
LOG_LEVEL = {
    10: "DEBUG",
    20: "INFO",
    30: "WARNING",
    40: "ERROR",
    50: "FATAL/CRITICAL/EXCEPTION"
}

PATTERN_JSON_FORMAT = r'^\{.*\}'

CONFIG_FILE_SECTION_NAME = 'FORMATTER'

_logFilePath = ""
def ReadConfig():
    global _logFilePath
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.abspath(__file__)) + os.sep + 'setting.cfg')
    config.sections()
    if 'DEFAULT' in config:
        _logFilePath = config.get(CONFIG_FILE_SECTION_NAME, 'ANSIBLE_LOG_PATH') + '*'

if __name__ == '__main__':
    # app log
    with open('logging_setting.json') as f:
        dictConfig(json.load(f))
    log = getLogger('logfile_formatter')
    log.info("The log level setting is {0}.".format(LOG_LEVEL[log.level]))
    startDatetime = DT.now()
    log.info("{0} {1} START".format(os.path.basename(__file__), startDatetime))

    log.info("アプリケーション設定の読込")
    ReadConfig()

    regex_json = re.compile(PATTERN_JSON_FORMAT)

    files = glob.glob(_logFilePath)
    cnt = 0
    for logfile in files:
        log.info("[{0}]を処理しています".format(logfile))
        cnt = cnt + 1
        with open(logfile, 'r') as hf:
            rowdata = hf.readline()
            rowcnt = 1
            while rowdata:
                cols = rowdata.split('-')
                if len(cols) == 3:
                    logDateTime = DT.strptime(cols[0].strip(), '%b %d %Y %H:%M:%S')
                    logStatus = cols[1]
                    try:
                        json_message = cols[2].split('=>')
                        for msg in json_message:
                            msg = msg.strip()
                            msg = msg.replace('\n', '')
                            if regex_json.match(msg):
                                logmsg = json.loads(msg)
                    except json.JSONDecodeError as e:
                        log.error(e.msg)

                rowdata = hf.readline()
                rowcnt = rowcnt + 1

    endDatetime = DT.now()
    log.info("{0} {1} END".format(os.path.basename(__file__), endDatetime))
    log.info("処理時間:{0}".format(endDatetime - startDatetime))
