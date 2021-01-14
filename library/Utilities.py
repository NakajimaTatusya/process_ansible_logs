#!/usr/bin/python3
# coding:utf-8

import os
import re
import codecs

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
