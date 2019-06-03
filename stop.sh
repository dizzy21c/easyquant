#!/bin/bash
ps -ef|grep mytest | grep -v grep | awk '{print $2}' | xargs kill -9

ps -ef|grep mydata | grep -v grep | awk '{print $2}' | xargs kill -9

ps -ef|grep mywatch | grep -v grep | awk '{print $2}' | xargs kill -9

