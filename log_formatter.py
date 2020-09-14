#!/usr/bin/python3
# coding:utf-8

import configparser
import glob
import os
import json
import pprint

#from collection import OrderedDict
from datetime import datetime as DT
from library import decode_unicode_escape

_logFilePath = ""

def ReadConfig():
    global _logFilePath
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.abspath(__file__)) + '/setting.cfg')
    config.sections()
    if 'DEFAULT' in config:
        _logFilePath = config.get('DEFAULT', 'LOG_FILE_DIR') + '*'

if __name__ == '__main__':
    nowdatetime = DT.now()
    print(nowdatetime.strftime('%b %d %Y %H:%M:%S'))
    ReadConfig()
    files = glob.glob(_logFilePath)

    cnt = 0
    for logfile in files:
        if cnt > 1:
            break
        print(logfile)
        cnt = cnt + 1
        with open(logfile, 'r') as hFile:
            rowdata = hFile.readline()
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

                rowdata = hFile.readline()
                rowcnt = rowcnt + 1
                print("行カウンター：{0}".format(rowcnt))
