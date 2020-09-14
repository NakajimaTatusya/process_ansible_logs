#!/usr/bin/python3
# coding:utf-8

import re
import codecs

PATTERN_UNICODE_ESCAPE = r'\\u([0-9]|[a-z]){4}'

def decode_unicode_escape(encode_string):
    """
    name属性に日本語（Multi byte）を使用すると、unicode-escape されるので戻す処理
    """
    decode_string = encode_string
    matchs = re.finditer(r'\\u([0-9]|[a-z]){4}', encode_string)
    for wk in matchs:
        decode_string = decode_string.replace(wk.group(), codecs.decode(wk.group(), 'unicode-escape'))
    return decode_string
