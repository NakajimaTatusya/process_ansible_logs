#!/usr/bin/python3
# coding:utf-8

import codecs
from datetime import datetime as DT
import glob
import os
import re

PATTERN_UNICODE_ESCAPE = r'\\u([0-9]|[a-z]){4}'


class PathOperator:
    @staticmethod
    def getFilenameWithoutExtension(path: str):
        return os.path.splitext(os.path.basename(path))[0]

    @staticmethod
    def getDirWithoutFilename(path: str):
        return os.path.dirname(path) + os.sep

    @staticmethod
    def partialExtraction(path: str):
        return ''.join(re.findall('win.*\.', path))[:-1]

    @staticmethod
    def getFilefullpathList(path: str, filedate: str = None):
        """
        summary:
            対象のディレクトリパスから、ファイルリストを作成して返す
            filedateパラメータが指定されていない場合は、実行日を設定する（YYYYMMDD）
        args:
            path: パス（*.logなどを指定可能）
            filedate: YYYYMMDD形式で文字列指定すると、ファイル名に含まれる日付でフィルタ
        """
        if not filedate:
            filedate = DT.now().strftime('%Y%m%d')
        return [x for x in glob.glob(pathname=path) if re.search(f".*{(filedate)}.*", x)]


class UnicodeEscape:
    @staticmethod
    def decode_unicode_escape(encode_string):
        """
        name属性に日本語（Multi byte）を使用すると、unicode-escape されるので戻す処理
        """
        decode_string = encode_string
        matchs = re.finditer(r'\\u([0-9]|[a-z]){4}', encode_string)
        for wk in matchs:
            decode_string = decode_string.replace(
                wk.group(), codecs.decode(wk.group(), 'unicode-escape'))
        return decode_string
