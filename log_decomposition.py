#!/usr/bin/python3
# coding:utf-8

"""
ansible 標準出力のログをフォーマットする
 strategy : linear strategy
"""

# pip install configparser
import configparser
import os
import glob
import re
import json
# pip install pyyaml
import yaml
import pprint

from datetime import datetime as DT
from datetime import timedelta as TDELTA

from library import decode_unicode_escape
from library import TaskLog
from library import TaskInfo
from library import Result
from library import Results

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

_stdout_logs_path = ""
_output_logs_path = ""
_ansible_hosts_path = ""
def ReadConfig():
    global _stdout_logs_path
    global _output_logs_path
    global _ansible_hosts_path
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.abspath(__file__)) + '/setting.cfg')
    config.sections()
    if 'DEFAULT' in config:
        _stdout_logs_path = config.get('DEFAULT', 'LOG_FILE_PLACE') + '*'
        _output_logs_path = config.get('DEFAULT', 'OUTPUT_MD_LOG')
        _ansible_hosts_path = config.get('DEFAULT', 'ANSIBLE_HOSTS_FILE_PATH')


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
            tmp = Result.Result()
            tmp.fieldName = key
            tmp.fieldValue = json[key]
            strage.addInfo(tmp)

def _getHostsList(obj, targetkey, lst):
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
    # アプリケーション設定読込
    ReadConfig()

    # 正規表現パターンを事前コンパイル
    regex_play = re.compile(PATTERN_PLAY)
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

            # TASK実行結果一覧表
            listTaskResult = os.path.splitext(os.path.basename(logfile))[0]
            taskListPath = "{0}Result_{1}.md".format(_output_logs_path, listTaskResult)
            with open(taskListPath, 'w') as hFnd:
                title = "# タスク実行結果リスト\n\n"
                hFnd.write(title)
                subtitle = "## 整形対象ファイル名：{0}\n\n".format(tasks.getLogFileName())
                hFnd.write(subtitle)
                hFnd.write(tasks.getTaskResultList())

            # タスク実行結果詳細出力
            # ホストごとにファイルを出力
            # read hosts
            with open(_ansible_hosts_path, 'r') as hYnd:
                obj = yaml.safe_load(hYnd)
                hosts = list()
                _getHostsList(obj, _group_name, hosts)
                
                for host in hosts:
                    taskDetailPath = "{0}Result_{1}_Detail.md".format(_output_logs_path, host)

                    with open(taskDetailPath, 'w') as f:
                        title = "# {0} - タスク実行結果詳細\n\n".format(host)
                        f.write(title)
                        subtitle = "## 整形対象ファイル名：{0}\n\n".format(tasks.getLogFileName())
                        f.write(subtitle)

                        for entity in filter(lambda x: x.hostname == host, tasks.row_data):
                            infos = Results.Results()
                            f.write(str(entity))
                            if entity.message != {}:
                                _recursively(entity.message, infos)
                                f.write(str(infos))
