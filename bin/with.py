#! /usr/bin python
# -*- coding:utf-8 -*-

#使用with读取文件
with open('../conf/jogos_web','r') as fread:
    for line in fread.readlines():
        print line.strip()


