#!/usr/bin/python3
# coding:utf-8

"""
ansible 標準出力のログをフォーマットする
 strategy : linear strategy
"""

import configparser
import os
import glob
import re
import json

from datetime import datetime as DT
from datetime import timedelta as TDELTA
from library import decode_unicode_escape
from library import TaskLog
from library import TaskInfo

# ログのTASK行をマッチング
PATTERN_TASK_ROW = r'^TASK \[.*\]'
# ログの実行日時行にマッチング
PATTERN_TASK_DATETIME = r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) (0[1-9]|[12][0-9]|3[01]) (January|February|March|April|May|June|July|August|September|October|November|December) [0-9]{4}  ([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]'
PATTERN_TASK_ELAPSED_TIME = r'[^(][0-9]:[0-5][0-9]:[0-5][0-9].[0-9]{3}[^)]'
# 実行結果とホスト名
PATTERN_STATUS_HOSTNAME = r'^.*: \[.*\]$'
# ログのJSON情報にマッチング
PATTERN_JSON_INFO_START = r'^.*: \[.*\].*=> {'
PATTERN_JSON_INFO_END = r'^\}$'
PATTERN_DELETE_ANSIBLE_SGIN = r'^.*: \[.*\] => '

_stdout_logs_path = ""
def ReadConfig():
    global _stdout_logs_path
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.abspath(__file__)) + '/setting.cfg')
    config.sections()
    if 'DEFAULT' in config:
        _stdout_logs_path = config.get('DEFAULT', 'LOG_FILE_PLACE') + '*'


class InformationEntity:
    def __init__(self):
        self.fieldName = ""
        self.fieldValue = ""

    def __str__(self):
        return "| {0} | {1} |\n".format(self.fieldName, self.fieldValue)


class InformationEntities:
    IndexCount = 0

    def __init__(self):
        self.data = []

    def addInfo(self, info):
        self.data.append(info)
        self.IndexCount += 1

    def __str__(self):
        strWk = "| 項目名 | 値 |\n"
        strWk += "| :--- | :--- |\n"
        for info in self.data:
            strWk += info.__str__()
        return strWk

    def getIndedxCount(self):
        return self.IndexCount


def _recursively(json, strage):
    for key in json:
        if isinstance(json[key], dict):
            _recursively(json[key], strage)
        elif isinstance(json[key], list):
            work_dic = {}
            index = 0
            for val in json[key]:
                work_dic[index] = val
                index = index + 1
            _recursively(work_dic, strage)
        elif key == 'stdout':
            pass
        else:
            tmp = InformationEntity()
            tmp.fieldName = key
            tmp.fieldValue = json[key]
            strage.addInfo(tmp)


if __name__ == '__main__':
    # アプリケーション設定読込
    ReadConfig()

    # 正規表現パターンを事前コンパイル
    regex_task = re.compile(PATTERN_TASK_ROW)
    regex_taskdate = re.compile(PATTERN_TASK_DATETIME)
    regex_elapsed = re.compile(PATTERN_TASK_ELAPSED_TIME)
    regex_result = re.compile(PATTERN_STATUS_HOSTNAME)
    regex_json_start = re.compile(PATTERN_JSON_INFO_START)
    regex_json_end = re.compile(PATTERN_JSON_INFO_END)

    stdout_log_files = glob.glob(_stdout_logs_path)
    for logfile in stdout_log_files:
        with open(logfile, 'r') as fHnd:
            row_data = fHnd.readline()
            tasks = TaskLog.TaskLog()
            tasks.log_file_name = logfile
            n_order = 0

            _taskname = ""
            _exec_datetime = DT.now()
            _elasped = TDELTA()
            json_start_flg = False
            str_json = ""

            while row_data:
                # 実行したタスク名
                if regex_task.match(row_data):
                    start_pos = row_data.find('[') + 1
                    end_pos = row_data.find(']')
                    _taskname = row_data[start_pos:end_pos]

                # いつ実行したか
                if regex_taskdate.match(row_data):
                    # 日時の取得
                    #print(row_data)
                    _exec_datetime = DT.strptime(regex_taskdate.match(row_data).group(0), '%A %d %B %Y %H:%M:%S')
                    # playbook開始からの経過時間
                    wkstr = regex_elapsed.search(row_data).group(0)
                    _elasped = TDELTA(
                        days = 0,
                        seconds = int(wkstr.split(':')[2].split('.')[0]),
                        microseconds = 0,
                        milliseconds = int(wkstr.split(':')[2].split('.')[1]),
                        minutes = int(wkstr.split(':')[1]),
                        hours = int(wkstr.split(':')[0]),
                        weeks = 0
                    )

                # 実行結果、リモートホスト名
                if regex_result.match(row_data):
                    taskinfo = TaskInfo.TaskInfo()
                    tasks.addRow(taskinfo)
                    n_order += 1

                    wk = regex_result.match(row_data).group(0).split(':')
                    tasks.row_data[n_order - 1].task_order = n_order
                    tasks.row_data[n_order - 1].hostname = wk[1][2:wk[1].find(']')]
                    tasks.row_data[n_order - 1].name = _taskname
                    tasks.row_data[n_order - 1].result_status = wk[0]
                    tasks.row_data[n_order - 1].exec_datetime = _exec_datetime
                    tasks.row_data[n_order - 1].elasped = _elasped

                # JSON形式の情報
                if json_start_flg:
                    str_json += row_data

                if regex_json_start.match(row_data):
                    taskinfo = TaskInfo.TaskInfo()
                    tasks.addRow(taskinfo)
                    n_order += 1
                    json_start_flg = True
                    str_json = "{"

                    wk = regex_json_start.match(row_data).group(0).split(':')
                    tasks.row_data[n_order - 1].task_order = n_order
                    tasks.row_data[n_order - 1].hostname = wk[1][2:wk[1].find(']')]
                    tasks.row_data[n_order - 1].name = _taskname
                    tasks.row_data[n_order - 1].result_status = wk[0]
                    tasks.row_data[n_order - 1].exec_datetime = _exec_datetime
                    tasks.row_data[n_order - 1].elasped = _elasped

                if regex_json_end.match(row_data):
                    json_start_flg = False
                    tasks.row_data[n_order - 1].message = json.loads(str_json)
                
                row_data = fHnd.readline()

            with open('test_result.md', 'w') as f:
                title = "# 整形対象ファイル名：{0}\n".format(tasks.getLogFileName())
                f.write(title)
                f.write("\n")

                for entity in tasks.row_data:
                    infos = InformationEntities()
                    f.write(str(entity))
                    if entity.message != {}:
                        _recursively(entity.message, infos)
                        f.write(str(infos))
