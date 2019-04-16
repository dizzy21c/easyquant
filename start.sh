#!/bin/bash
ps -ef|grep mytest | grep -v grep | awk '{print $2}' |xargs kill -9
cd /home/zhangjx/backup/bk/easyquant
/home/zhangjx/anaconda3/bin/python mytest.py  &

