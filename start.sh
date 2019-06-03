#!/bin/bash

ps -ef|grep mydata | grep -v grep | awk '{print $2}' |xargs kill -9
ps -ef|grep mywatch | grep -v grep | awk '{print $2}' |xargs kill -9

cd /home/zhangjx/backup/bk/easyquant
/home/zhangjx/anaconda3/bin/python mydata.py  &
/home/zhangjx/anaconda3/bin/python mywatch.py  &

