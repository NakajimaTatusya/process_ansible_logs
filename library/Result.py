#!/usr/bin/python3
# coding:utf-8

class Result:
    def __init__(self):
        self.fieldName = ""
        self.fieldValue = ""

    def __str__(self):
        return "| {0} | {1} |\n".format(self.fieldName, self.fieldValue)

    def getTSV(self):
        return "{0}\t{1}\n".format(self.fieldName, self.fieldValue)
