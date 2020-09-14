#!/usr/bin/python3
# coding:utf-8

"""
JSON オブジェクトを読み込む
項目を TREE で表示する
"""

import configparser
import glob
import os
from datetime import datetime as DT
import json
import pprint

ROOT_NAME = 'ANSIBLE_LOG'

test = """
{"dict": {"192.168.1.202": {"hostname": "192.168.1.202", "ipv4": "192.168.1.202", "subet": "255.255.255.0", "defaultgateway": "192.168.1.1", "dns1": "192.168.1.1", "dns2": "192.168.1.2", "workgroupname": "ansiblewkg", "memo": "abc"}, "192.168.1.203": {"hostname": "192.168.1.203", "ipv4": "192.168.1.203", "subet": "255.255.255.0", "defaultgateway": "192.168.1.1", "dns1": "192.168.1.1", "dns2": "192.168.1.2", "workgroupname": "ansiblewkg", "memo": "def"}, "192.168.1.204": {"hostname": "192.168.1.204", "ipv4": "192.168.1.204", "subet": "255.255.255.0", "defaultgateway": "192.168.1.1", "dns1": "192.168.1.1", "dns2": "192.168.1.2", "workgroupname": "ansiblewkg", "memo": "ghi"}, "192.168.1.205": {"hostname": "192.168.1.205", "ipv4": "192.168.1.205", "subet": "255.255.255.0", "defaultgateway": "192.168.1.1", "dns1": "192.168.1.1", "dns2": "192.168.1.2", "workgroupname": "ansiblewkg", "memo": "jkl"}}, "list": [], "_ansible_no_log": false, "changed": false, "_ansible_delegated_vars": {"ansible_host": "localhost"}}"""
json_file = '{ "name": "John", "items": [ { "item_name": "lettuce", "price": 2.65, "units": "no" }, { "item_name": "ketchup", "price": 1.51, "units": "litres" } ] }'


class TreeNode(object):
    """
    Tree Node
    """
    def __init__(self, data):
        self.data = data
        self.children = []

    def add_child(self, obj):
        self.children.append(obj)

    def __str__(self, level=0):
        ret = "\t" * level + repr(self.data) + "\n"
#        if level == 2:
#            ret = "\t" * level + repr(self.data)
#        elif level == 4:
#            ret = "\t" + repr(self.data) + "\n"
#        else:
#            ret = "\t" * level + repr(self.data) + "\n"
        for child in self.children:
            ret += child.__str__(level+1)
        return ret

    def __repr__(self):
        return '<tree node representation>'


class Tree:
    """
    Tree
    """
    def __init__(self):
        self.root = TreeNode(ROOT_NAME)

    def __str__(self):
        return self.root.__str__()


def create_tree_from_JSON(json):
    """
    Treeの根を作る
    """
    tree = Tree()
    node_0 = TreeNode(ROOT_NAME)
    tree.root = node_0
    parent = node_0
    _walk_tree(json, parent)
    return tree


def _walk_tree(json, parent):
    """
    枝葉を再帰的に作成
    ただし、配列は添え字を使う
    """
    for key in json:
        if isinstance(json[key], dict):
            head = TreeNode(key)
            parent.add_child(head)
            _walk_tree(json[key], head)
        elif isinstance(json[key], list):
            head = TreeNode(key)
            parent.add_child(head)
            work_dic = {}
            index = 0
            for val in json[key]:
                work_dic[index] = val
                index = index + 1
            _walk_tree(work_dic, head)
        else:
            node = TreeNode(key)
            node.add_child(TreeNode(json[key]))
            parent.add_child(node)


if __name__ == '__main__':
    with open('test.json', 'r') as f:
        product = f.read()
    temp = json.loads(product, strict=False)
#    temp = json.loads(test)
#    temp = json.loads(json_file)
    t = create_tree_from_JSON(temp)
    print(t)
    with open('formatted_log.txt', 'w') as wf:
        wf.write(str(t))
