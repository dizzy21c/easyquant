#!/bin/bash
ps -ef|grep mydata2 | grep -v grep | awk '{print $2}' |xargs kill -9
ps -ef|grep mycalc | grep -v grep | awk '{print $2}' |xargs kill -9

cd /home/zhangjx/backup/bk/easyquant
dt=`date +%H%M`
if [ $dt -lt "0930" ]; then
  rm -rf logs/*
fi
# echo "calc top-codes..."
# /home/zhangjx/anaconda3/bin/python codelist_utils.py --code_type=top-codes
echo "start data-monitoring"
/home/zhangjx/anaconda3/envs/qawork/bin/python mydata2.py &
echo "start calc-monitoring"
#calc-day-data, calc-min-data,calc-day-data-idx
##/home/zhangjx/anaconda3/envs/qawork/bin/python mycalc.py --calc-name calc-day-data &
##/home/zhangjx/anaconda3/envs/qawork/bin/python mycalc.py --calc-name calc-min-data &
##/home/zhangjx/anaconda3/envs/qawork/bin/python mycalc.py --calc-name calc-day-index &
#/home/zhangjx/anaconda3/bin/python mydata2.py  &

/home/zhangjx/anaconda3/envs/qawork/bin/python simple-strategies/positions_01.py &
