#!/bin/bash
#work1=`ps -ef|grep mytest | grep -v grep | awk '{print $2}'`
work1=`ps -ef|grep mydata | grep -v grep | awk '{print $2 "," }'`
work2=`ps -ef|grep myworker | grep -v grep | awk '{print $2 "," }' | xargs ` 
if [ "x$work1" == "x"  -a  "x$work2" == "x" ]; then
  exit 0
fi
if [ "x$work1" == "x" ]; then
  echo wk2 $work2
  top -H -p $work2 99999
  exit 0
fi
if [ "x$work2" == "x" ]; then
  echo wk1 $work1
  top -H -p $work1 99999
  exit 0
fi
echo wka $work1 $work2
top -H -p $work1 $work2 99999

