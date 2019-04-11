# coding:utf8
import json
import os
import re

import requests

STOCK_CODE_PATH = "config/stock_codes.conf"


def update_stock_codes():
    """获取所有股票 ID 到 all_stock_code 目录下"""
    all_stock_codes_url = "http://www.shdjt.com/js/lib/astock.js"
    grep_stock_codes = re.compile("~(\d+)`")
    response = requests.get(all_stock_codes_url)
    all_stock_codes = grep_stock_codes.findall(response.text)
    with open(stock_code_path(), "w") as f:
        f.write(json.dumps(dict(stock=all_stock_codes)))


def get_stock_codes():
    """获取所有股票 ID 到 all_stock_code 目录下"""
    all_stock_codes_url = "http://www.shdjt.com/js/lib/astock.js"
    response = requests.get(all_stock_codes_url)
    
    stocks=[]
    gre = re.compile("~(000\d+)`")
    codes = gre.findall(response.text)
    stocks=stocks+codes
    gre = re.compile("~(001\d+)`")
    codes2 = gre.findall(response.text)
    stocks=stocks+codes2
    with open(stock_code_path("sz_list.json"), "w") as f:
        f.write(json.dumps(dict(code=codes + codes2)))

    gre = re.compile("~(002\d+)`")
    codes = gre.findall(response.text)
    stocks=stocks+codes
    with open(stock_code_path("zxb_list.json"), "w") as f:
        f.write(json.dumps(dict(code=codes)))

    gre = re.compile("~(30\d+)`")
    codes = gre.findall(response.text)
    stocks=stocks+codes
    with open(stock_code_path("cyb_list.json"), "w") as f:
        f.write(json.dumps(dict(code=codes)))

    gre = re.compile("~(6\d+)`")
    codes = gre.findall(response.text)
    stocks=stocks+codes
    with open(stock_code_path("sh_list.json"), "w") as f:
        f.write(json.dumps(dict(code=codes)))

    with open(stock_code_path("stock_list.json"), "w") as f:
        f.write(json.dumps(dict(code=stocks)))

    gre = re.compile("~(39\d+)`")
    codes = gre.findall(response.text)
    gre = re.compile("~(sh\d+)`")
    codes2 = gre.findall(response.text)
    with open(stock_code_path("index_list.json"), "w") as f:
        f.write(json.dumps(dict(code=codes+codes2)))

    gre = re.compile("~(99\d+)`")
    codes = gre.findall(response.text)
    with open(stock_code_path("bk_list.json"), "w") as f:
        f.write(json.dumps(dict(code=codes)))


    return "ok"


def stock_code_path(fileName):
    return os.path.join(os.path.dirname(__file__), "config", fileName)

get_stock_codes()

