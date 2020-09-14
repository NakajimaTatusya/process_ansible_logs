#!/usr/bin/python3
# coding:utf-8

import os
import glob
import re

from library import decode_unicode_escape

# ログのTASK行をマッチング
PATTERN_TASK_ROW = r'^TASK \[.*\]'
# ログの実行日時行にマッチング
PATTERN_RUN_DATETIME = r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) (0[1-9]|[12][0-9]|3[01]) (January|February|March|April|May|June|July|August|September|October|November|December)'
# ログのJSON情報にマッチング
PATTERN_JSON_INFO_START = r'^.*: \[.*\] => {$'
PATTERN_JSON_INFO_END = r'^\}$'
PATTERN_DELETE_ANSIBLE_SGIN = r'^.*: \[.*\] => '

_stdout_logs_path = "/home/tnakajima/challenges_ansible/*.log"

if __name__ == '__main__':
    stdout_log_files = glob.glob(_stdout_logs_path)
    for logfile in stdout_log_files:
        print(logfile)

    with open('/home/tnakajima/challenges_ansible/20200825-01_windows-common.log', 'r') as fHnd:
        row_data = fHnd.readline()
        while row_data:
            if re.match(PATTERN_TASK_ROW, row_data):
                print(row_data)
            if re.match(PATTERN_RUN_DATETIME, row_data):
                print(row_data)
            if re.match(PATTERN_JSON_INFO_START, row_data):
                print(row_data)
                wk = row_data
                print(re.match(PATTERN_DELETE_ANSIBLE_SGIN, wk).group())
                print(wk.replace(re.match(PATTERN_DELETE_ANSIBLE_SGIN, wk).group(), ''))
            if re.match(PATTERN_JSON_INFO_END, row_data):
                print(row_data)
            
            row_data = fHnd.readline()
