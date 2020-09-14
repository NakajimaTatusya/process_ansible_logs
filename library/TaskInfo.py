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
        return "## {0}\t{1}\t{2}\t{3}\t{4}\t{5}\n".format(self.task_order, self.hostname, self.name, self.result_status, self.exec_datetime, self.elasped)

    def getJsonStr(self):
        return json.dumps(self.message)
