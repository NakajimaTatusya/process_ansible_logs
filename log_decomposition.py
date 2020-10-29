#!/usr/bin/python3
# coding:utf-8

"""
ansible 標準出力のログをフォーマットする
 strategy : linear strategy
"""

import aiofiles #pip install aiofiles
import asyncio
from collections import deque
import configparser # pip install configparser
import glob

from logging.config import dictConfig
from logging import getLogger

import markdown
import sys
import json
import os
import pprint
import re
import yaml # pip install pyyaml

from datetime import datetime as DT
from datetime import timedelta as TDELTA

from library import Result
from library import Results
from library import TaskLog
from library import TaskInfo
from library import StyleSheet
from library import Utilities

# ログレベル定義
LOG_LEVEL = {
    10: "DEBUG",
    20: "INFO",
    30: "WARNING",
    40: "ERROR",
    50: "FATAL/CRITICAL/EXCEPTION"
}

# ハンドラーをオーバーライドできれば、ログファイルに影響を与えずにコンソール出力の文字色を変更できると思われる
#def set_color(org_string, level=None):
#    color_levels = {
#        10: "\033[36m{}\033[0m",       # DEBUG
#        20: "\033[32m{}\033[0m",       # INFO
#        30: "\033[33m{}\033[0m",       # WARNING
#        40: "\033[31m{}\033[0m",       # ERROR
#        50: "\033[7;31;31m{}\033[0m"   # FATAL/CRITICAL/EXCEPTION
#    }
#    if level is None:
#        return color_levels[20].format(org_string)
#    else:
#        return color_levels[int(level)].format(org_string)

# Play 行にマッチング
PATTERN_PLAY = r'^PLAY \[.*\]'
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

CONFIG_FILE_SECTION_NAME = 'DECOMPOSITION'

_stdout_logs_path = ""
_output_md_path = ""
_output_html_path = ""
_ansible_hosts_path = ""
def ReadConfig():
    """
    このアプリの設定を読み込む
    """
    global _stdout_logs_path
    global _output_md_path
    global _output_html_path
    global _ansible_hosts_path
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.abspath(__file__)) + os.sep + 'setting.cfg')
    config.sections()
    if 'DEFAULT' in config:
        _stdout_logs_path = config.get(CONFIG_FILE_SECTION_NAME, 'LOG_FILE_PLACE') + '*.log'
        _output_md_path = config.get(CONFIG_FILE_SECTION_NAME, 'OUTPUT_MD_FILES')
        _output_html_path = config.get(CONFIG_FILE_SECTION_NAME, 'OUTPUT_HTML_FILES')
        _ansible_hosts_path = config.get(CONFIG_FILE_SECTION_NAME, 'ANSIBLE_HOSTS_FILE_PATH')


data_que = deque()
async def write_file(file: str):
    """
    MD、HTMLを非同期出力する
    """
    style = StyleSheet.LogStyle()
    wdata = data_que.popleft()
    async with aiofiles.open(file, mode='w') as f:
        await f.write(wdata)
    md = markdown.Markdown(extensions=['tables'])
    html = style.header + md.convert(wdata) + style.footer
    htmlpath = "{0}{1}.html".format(_output_html_path, Utilities.PathOperator.getFilenameWithoutExtension(file))
    async with aiofiles.open(htmlpath, mode='w') as f:
        await f.write(html)


def _recursively(json, strage):
    """
    JSON を再帰処理で分解
    """
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
            tmp = Result.Result()
            tmp.fieldName = key
            tmp.fieldValue = json[key]
            strage.addInfo(tmp)


def _getHostsList(obj, targetkey, lst):
    """
    Ansible Inventory File(YAML) から実行対象ホスト一覧を取得する
    """
    for key in obj:
        if key == targetkey:
            wobj = obj[key]
            for host in wobj['hosts']:
                lst.append(host)
        else:
            if isinstance(obj[key], dict):
                _getHostsList(obj[key], targetkey, lst)
            elif isinstance(obj[key], list):
                work_dic = {}
                index = 0
                for val in obj[key]:
                    work_dic[index] = val
                    index = index + 1
                _getHostsList(work_dic, targetkey, lst)


if __name__ == '__main__':
    # app log
    with open('logging_setting.json') as f:
        dictConfig(json.load(f))
    log = getLogger('log_decomposition')
    log.info("The log level setting is {0}.".format(LOG_LEVEL[log.level]))
    startDatetime = DT.now()
    log.info("{0} {1} START".format(os.path.basename(__file__), startDatetime))

    log.info("アプリケーション設定の読込")
    ReadConfig()

    log.info("正規表現パターンを事前コンパイル")
    regex_play = re.compile(PATTERN_PLAY)
    regex_task = re.compile(PATTERN_TASK_ROW)
    regex_taskdate = re.compile(PATTERN_TASK_DATETIME)
    regex_elapsed = re.compile(PATTERN_TASK_ELAPSED_TIME)
    regex_result = re.compile(PATTERN_STATUS_HOSTNAME)
    regex_json_start = re.compile(PATTERN_JSON_INFO_START)
    regex_json_end = re.compile(PATTERN_JSON_INFO_END)

    stdout_log_files = glob.glob(_stdout_logs_path)
    for logfile in stdout_log_files:
        if os.path.isfile(logfile) != True:
            continue
        log.info("ファイル名：{0} を処理しています".format(logfile))
        with open(logfile, 'r') as fHnd:
            row_data = fHnd.readline()
            tasks = TaskLog.TaskLog()
            tasks.log_file_name = logfile
            n_order = 0

            _group_name = ""
            _taskname = ""
            _exec_datetime = DT.now()
            _elasped = TDELTA()
            json_start_flg = False
            str_json = ""

            while row_data:
                # 実行しているグループ名を取得する処理
                if regex_play.match(row_data):
                    start_pos = row_data.find('[') + 1
                    end_pos = row_data.find(']')
                    _group_name = row_data[start_pos:end_pos]

                # 実行したタスク名
                if regex_task.match(row_data):
                    start_pos = row_data.find('[') + 1
                    end_pos = row_data.find(']')
                    _taskname = row_data[start_pos:end_pos]

                # いつ実行したか
                if regex_taskdate.match(row_data):
                    # 日時の取得
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

            log.info("タスク実行結果一覧表を出力します")
            tasklist = "# タスク実行結果リスト\n\n"
            tasklist += "## 取込ログファイル名：{0}\n\n".format(tasks.getLogFileName())
            tasklist += tasks.getTaskResultList()

            listTaskResult = Utilities.PathOperator.getFilenameWithoutExtension(logfile)
            taskListPath = "{0}Result_{1}.md".format(_output_md_path, listTaskResult)
            data_que.append(tasklist)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(write_file(taskListPath))

            log.info("タスク実行結果詳細をホストごとに出力します")
            with open(_ansible_hosts_path, 'r') as hYnd:
                obj = yaml.safe_load(hYnd)
                hosts = list()
                _getHostsList(obj, _group_name, hosts)
                
                for host in hosts:
                    contents = ""
                    contents = "# {0} - タスク実行結果詳細\n\n".format(host)
                    contents += "## 取込ログファイル名：{0}\n\n".format(tasks.getLogFileName())

                    for entity in filter(lambda x: x.hostname == host, tasks.row_data):
                        infos = Results.Results()
                        if entity.message != {}:
                            contents += str(entity)
                            _recursively(entity.message, infos)
                            contents += str(infos)

                    taskDetailPath = "{0}Result_{1}_Detail.md".format(_output_md_path, host)
                    data_que.append(contents)
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(write_file(taskDetailPath))

    endDatetime = DT.now()
    log.info("{0} {1} END".format(os.path.basename(__file__), endDatetime))
    log.info("処理時間:{0}".format(endDatetime - startDatetime))
