#!/bin/bash
ps -ef|grep mydata | grep -v grep | awk '{print $2}' | xargs kill
ps -ef|grep mywatch | grep -v grep | awk '{print $2}' | xargs kill

