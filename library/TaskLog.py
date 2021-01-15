#!/usr/bin/python3
# coding:utf-8

class TaskLog:
    def __init__(self):
        self.row_data = list()
        self.log_file_name = ""

    def addRow(self, data):
        self.row_data.append(data)

    def getTaskResultList(self):
        constOK = "| {0} | {1} | {2} | {3} | {4} | {5} |\n"
        constSkipping = '| <span style="color: blue; ">{0}</span> | <span style="color: blue; ">{1}</span> | <span style="color: blue; ">{2}</span> | <span style="color: blue; ">{3}</span> | <span style="color: blue; ">{4}</span> | <span style="color: blue; ">{5}</span> |\n'
        constChanged = '| <span style="color: green; ">{0}</span> | <span style="color: green; ">{1}</span> | <span style="color: green; ">{2}</span> | <span style="color: green; ">{3}</span> | <span style="color: green; ">{4}</span> | <span style="color: green; ">{5}</span> |\n'
        constFatal = '| <span style="color: red; ">{0}</span> | <span style="color: red; ">{1}</span> | <span style="color: red; ">{2}</span> | <span style="color: red; ">{3}</span> | <span style="color: red; ">{4}</span> | <span style="color: red; ">{5}</span> |\n'
        strWk = "| # | HOSTNAME | TASK 名 | 結果 | 実行日時 | 経過時間 |\n"
        strWk += "| ---: | :--- | :--- | :--- | :--- | :--- |\n"
        for entity in self.row_data:
            if "fatal" == entity.result_status:
                strWk += constFatal.format(entity.task_order, entity.hostname, entity.name, entity.result_status, entity.exec_datetime, entity.elasped)
            elif "skipping" == entity.result_status:
                strWk += constSkipping.format(entity.task_order, entity.hostname, entity.name, entity.result_status, entity.exec_datetime, entity.elasped)
            elif "changed" == entity.result_status:
                strWk += constChanged.format(entity.task_order, entity.hostname, entity.name, entity.result_status, entity.exec_datetime, entity.elasped)
            else:
                strWk += constOK.format(entity.task_order, entity.hostname, entity.name, entity.result_status, entity.exec_datetime, entity.elasped)
        return strWk

    def getLogFileName(self):
        return self.log_file_name
