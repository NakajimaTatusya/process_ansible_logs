#!/usr/bin/python3
# coding:utf-8

class TaskLog:
    def __init__(self):
        self.row_data = list()
        self.log_file_name = ""

    def addRow(self, data):
        self.row_data.append(data)

    def getLogFileName(self):
        return self.log_file_name
