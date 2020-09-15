# Ansible の Log を加工する

* 家の PlayBook 実行方法に依存していると思われる、複雑なやり方に対応できるかは不明
* 標準出力のログ
* ログファイル

## 標準出力のログ

* 既定の出力を変換する

## ログファイル

* JSON 内容を加工する
* unicode_escape された日本語を戻す

## 目標

* MD File に加工する
* Excel File に加工する
* MD → Word 変換を行う
* 画面で参照できるようにする

## ソースコード

| ファイル名 | 内容 |
| :--- | :--- |
| json_to_tree.py | JSON を Tree に展開する |
| log_decomposition.py | 標準出力のログをファイルへ保存したものを整形する |
| log_formatter.py | ansible log ファイルを整形する |
| setting.cfg | アプリケーション設定ファイル |
| unicode_escape_to_character.py | unicode-escape されたマルチバイト文字列を元に戻す |

