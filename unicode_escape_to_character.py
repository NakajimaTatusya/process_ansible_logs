import codecs
import re

unicode_escape = "これから、\\u30d5\\u30a1\\u30a4\\u30eb\\u304b\\u3089\\u30d1\\u30e9\\u30e1「ちくわ大明神」\\u30fc\\u30bf\\u3092\\u53d6\\u5f97\\u3059\\u308b\\u30c6\\u30b9\\u30c8をします。"
decode_string = unicode_escape


result = re.finditer(r'\\u([0-9]|[a-z]){4}', unicode_escape)
for wk in result:
    #print(codecs.decode(wk.group(), 'unicode-escape'))
    #print("start {0}, end {1}".format(wk.start(), wk.end()))
    decode_string = decode_string.replace(wk.group(), codecs.decode(wk.group(), 'unicode-escape'))

print(decode_string)
