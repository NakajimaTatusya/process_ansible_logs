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

from jinja2 import Environment, FileSystemLoader

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
_output_md_path = ""
def ReadConfig():
    global _logFilePath
    global _output_md_path
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.abspath(__file__)) + os.sep + 'setting.cfg')
    config.sections()
    if 'DEFAULT' in config:
        _logFilePath = config.get(CONFIG_FILE_SECTION_NAME, 'ANSIBLE_LOG_PATH') + '*'
        _output_md_path = config.get(CONFIG_FILE_SECTION_NAME, 'OUTPUT_MD_FILES')

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

    log.info("JINJA2 テンプレート読込")
    env = Environment(loader=FileSystemLoader('./templates', encoding='utf8'))
    tmplate = env.get_template('ansible_syslog_hostname.md.j2')

    regex_json = re.compile(PATTERN_JSON_FORMAT)

    files = glob.glob(_logFilePath)
    cnt = 0
    for logfile in files:
        log.info("[{0}]を処理しています".format(logfile))
        j2_target_log = logfile
        hostname = logfile[logfile.rfind(os.sep) + 1:]
        j2_table_rows = []
        cnt = cnt + 1
        with open(logfile, 'r') as hf:
            rowdata = hf.readline()
            rowcnt = 1
            while rowdata:
                cols = rowdata.split('-')
                if len(cols) == 3:
                    j2_logDateTime = DT.strptime(cols[0].strip(), '%b %d %Y %H:%M:%S')
                    j2_logStatus = cols[1]
                    try:
                        json_message = cols[2].split('=>')
                        for j2_msg in json_message:
                            j2_msg = j2_msg.strip()
                            j2_msg = j2_msg.replace('\n', '')
                            if regex_json.match(j2_msg):
                                #log.debug(j2_msg)
                                #logmsg = json.loads(msg)
                                # --- json 見やすく加工する処理を書きましょう
                                j2_table_rows.append({'j2_logDateTime': j2_logDateTime, 'j2_logStatus': j2_logStatus, 'j2_msg': j2_msg })
                            else:
                                j2_table_rows.append({'j2_logDateTime': j2_logDateTime, 'j2_logStatus': j2_logStatus, 'j2_msg': j2_msg })
                    except json.JSONDecodeError as e:
                        log.error(e.msg)

                rowdata = hf.readline()
                rowcnt = rowcnt + 1

            md = tmplate.render({'j2_target_log': j2_target_log, 'j2_table_rows': j2_table_rows})
            # ファイルへ書き込み
            output_path = "{0}ansible_syslog_{1}.md".format(_output_md_path, hostname)
            log.debug(output_path)
            with open(output_path, 'w') as fw:
                fw.write(md)

    endDatetime = DT.now()
    log.info("{0} {1} END".format(os.path.basename(__file__), endDatetime))
    log.info("処理時間:{0}".format(endDatetime - startDatetime))
