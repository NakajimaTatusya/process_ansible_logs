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
    log.info("formatter {0} START".format(startDatetime))

    log.info("アプリケーション設定の読込")
    ReadConfig()

    files = glob.glob(_logFilePath)
    cnt = 0
    for logfile in files:
        if cnt > 1:
            break
        print(logfile)
        cnt = cnt + 1
        with open(logfile, 'r') as hf:
            rowdata = hf.readline()
            rowcnt = 1
            while rowdata:
#                print("読み取った行データ：{0}".format(rowdata))
                cols = rowdata.split('-')
                if len(cols) == 3:
#                    print('{0} {1} {2}'.format(cols[0], cols[1], cols[2]))
                    logDateTime = DT.strptime(cols[0].strip(), '%b %d %Y %H:%M:%S')
                    logStatus = cols[1]
                    print(cols[2])
                    try:
                        logmsg = json.loads(cols[2])
                    except json.JSONDecodeError as e:
                        logmsg = cols[2]

                    #pprint.pprint(logmsg)

                rowdata = hf.readline()
                rowcnt = rowcnt + 1
                print("行カウンター：{0}".format(rowcnt))

    endDatetime = DT.now()
    log.info("log_decomposition {0} END".format(endDatetime))
    log.info("処理時間:{0}".format(endDatetime - startDatetime))
