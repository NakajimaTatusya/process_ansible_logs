#!/usr/bin/python3
# coding:utf-8

class Results:
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
        strWk += "\n"
        return strWk

    def getTSV(self):
        strWk = "項目名\t値\n"
        for info in self.data:
            strWk += info.getTSV()
        return strWk

    def getIndedxCount(self):
        return self.IndexCount
