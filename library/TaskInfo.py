#!/usr/bin/python3
# coding:utf-8

import json

from datetime import datetime as DT
from datetime import timedelta as TDELTA

class TaskInfo:
    def __init__(self):
        self.task_order = 0
        self.hostname = ""
        self.name = ""
        self.result_status = ""
        self.exec_datetime = DT.now()
        self.elasped = TDELTA()
        self.message = {}

    def __str__(self):
        strWk = "| # | HOSTNAME | TASK 名 | 結果 | 実行日時 | 経過時間 |\n"
        strWk += "| ---: | :--- | :--- | :--- | :--- | :--- |\n"
        strWk += "| {0} | {1} | {2} | {3} |{4} | {5} |\n\n".format(self.task_order, self.hostname, self.name, self.result_status, self.exec_datetime, self.elasped)
        return strWk

    def getJsonStr(self):
        return json.dumps(self.message)
