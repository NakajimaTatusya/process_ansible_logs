import configparser
import glob
import os
from datetime import datetime as DT
import json
#from collection import OrderedDict
import pprint

ROOT_NAME = 'ANSIBLE_LOG'

test = """
{"dict": {"192.168.1.202": {"hostname": "192.168.1.202", "ipv4": "192.168.1.202", "subet": "255.255.255.0", "defaultgateway": "192.168.1.1", "dns1": "192.168.1.1", "dns2": "192.168.1.2", "workgroupname": "ansiblewkg", "memo": "abc"}, "192.168.1.203": {"hostname": "192.168.1.203", "ipv4": "192.168.1.203", "subet": "255.255.255.0", "defaultgateway": "192.168.1.1", "dns1": "192.168.1.1", "dns2": "192.168.1.2", "workgroupname": "ansiblewkg", "memo": "def"}, "192.168.1.204": {"hostname": "192.168.1.204", "ipv4": "192.168.1.204", "subet": "255.255.255.0", "defaultgateway": "192.168.1.1", "dns1": "192.168.1.1", "dns2": "192.168.1.2", "workgroupname": "ansiblewkg", "memo": "ghi"}, "192.168.1.205": {"hostname": "192.168.1.205", "ipv4": "192.168.1.205", "subet": "255.255.255.0", "defaultgateway": "192.168.1.1", "dns1": "192.168.1.1", "dns2": "192.168.1.2", "workgroupname": "ansiblewkg", "memo": "jkl"}}, "list": [], "_ansible_no_log": false, "changed": false, "_ansible_delegated_vars": {"ansible_host": "localhost"}}"""
json_file = '{ "name": "John", "items": [ { "item_name": "lettuce", "price": 2.65, "units": "no" }, { "item_name": "ketchup", "price": 1.51, "units": "litres" } ] }'


class TsvRow:
    def __init__(self):
        self.row = []

    def add_col(self, col):
        self.row.append(col)

    def __str__(self):
        cnt = 0
        ret = ""
        for col in self.row:
            if cnt == 0:
                ret = col
            else:
                ret += "\t" + col
            cnt += 1
        return ret


class Tsv:
    def __init__(self):
        self.table = []

    def addnew(self, col):
        self.table

    def __str__(self):
        cnt = 0
        ret = ""
#        for col in self.data:
#            print(col)
#            if cnt == 0:
#                ret += col
#            else:
#                ret += "\t" + col
#            cnt += 1
#        return ret


def create_tsv_from_JSON(json):  # root case
    tsv = Tsv()
    _walk_tsv(json, tsv)
    return tsv

def _walk_tsv(json, tsv):  # recursive case
    for key in json:
        if isinstance(json[key], dict):
            tsv.add_data(key)
            _walk_tsv(json[key], tsv)
        elif isinstance(json[key], list):
            tsv.add_data(key)
            work_dic = {}
            index = 0
            for val in json[key]:
                work_dic[index] = val
                index = index + 1
            _walk_tsv(work_dic, tsv)
        else:
            tsv.add_data(json[key])

if __name__ == '__main__':
    temp = json.loads(test)
#    temp = json.loads(json_file)
    t = create_tsv_from_JSON(temp)
    print(t)
