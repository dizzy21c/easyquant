#!/bin/bash

ps -ef|grep mydata | grep -v grep | awk '{print $2}' |xargs kill -9
ps -ef|grep myworker | grep -v grep | awk '{print $2}' |xargs kill -9

cd /home/zhangjx/backup/bk/easyquant

rm -rf logs/*

/home/zhangjx/anaconda3/bin/python mydata.py  &

/home/zhangjx/anaconda3/bin/python myworker.py data-worker &

/home/zhangjx/anaconda3/bin/python myworker.py index-worker &

/home/zhangjx/anaconda3/bin/python myworker.py position-worker &

