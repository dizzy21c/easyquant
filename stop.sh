#!/bin/bash
ps -ef|grep mytest | grep -v grep | awk '{print $2}' | xargs kill

