# coding:utf8
import json
import os
import re
import xlrd
import requests
from easyquant import QATdx as tdx

STOCK_CODE_PATH = "config/stock_codes.conf"


# def update_stock_codes():
#     all_stock_codes_url = "http://www.shdjt.com/js/lib/astock.js"
#     grep_stock_codes = re.compile("~(\d+)`")
#     response = requests.get(all_stock_codes_url)
#     all_stock_codes = grep_stock_codes.findall(response.text)
#     with open(stock_code_path(), "w") as f:
#         f.write(json.dumps(dict(stock=all_stock_codes)))

def get_udf_code_list(config="config/codelist.xlsx"):
    if config:
        data = xlrd.open_workbook(config)
        table = data.sheets()[0]
        rows_count = table.nrows
        black_codes = table.col_values(0)[1:rows_count]

        table = data.sheets()[1]
        rows_count = table.nrows
        index_codes = table.col_values(0)[1:rows_count]

        table = data.sheets()[2]
        rows_count = table.nrows
        block_codes = table.col_values(0)[1:rows_count]

        # names = table.col_values(1)[1:rows_count]
        # return list(zip(codes, names))
        return (black_codes, index_codes, block_codes)
    # else:
    #     data_files = os.listdir(settings.DATA_DIR)
    #     stocks = []
    #     for file in data_files:
    #         code_name = file.split(".")[0]
    #         code = code_name.split("-")[0]
    #         name = code_name.split("-")[1]
    #         appender = (code, name)
    #         stocks.append(appender)
    #     return stocks
def get_stock_codes():
    black_list,index_list,block_list= get_udf_code_list()
    codes_df = tdx.QA_fetch_get_stock_list()

    sz_stocks=[]
    zxb_stocks=[]
    cyb_stocks=[]
    sh_stocks=[]
    codes = list(codes_df['code'])
    for code in codes:
        if code in black_list:
            continue
        tmp = code[0:3]
        if tmp == "000" or tmp == "001":
            sz_stocks.append(code)
        elif tmp == "002":
            zxb_stocks.append(code)
        elif tmp == "300" or tmp == "301":
            cyb_stocks.append(code)
        else:
            sh_stocks.append(code)
        
    with open(stock_code_path("sz_list.json"), "w") as f:
        f.write(json.dumps(dict(code=sz_stocks)))
    
    with open(stock_code_path("zxb_list.json"), "w") as f:
        f.write(json.dumps(dict(code=zxb_stocks)))
    
    with open(stock_code_path("cyb_list.json"), "w") as f:
        f.write(json.dumps(dict(code=cyb_stocks)))
    
    with open(stock_code_path("sh_list.json"), "w") as f:
        f.write(json.dumps(dict(code=sh_stocks)))

    with open(stock_code_path("stock_list.json"), "w") as f:
        stock_list=[]
        stock_list=stock_list + sh_stocks
        stock_list=stock_list + sz_stocks
        stock_list=stock_list + cyb_stocks
        stock_list=stock_list + zxb_stocks
        f.write(json.dumps(dict(code=stock_list)))

    # index_df = tdx.QA_fetch_get_index_list()
    with open(stock_code_path("index_list.json"), "w") as f:
        f.write(json.dumps(dict(code=index_list)))

    with open(stock_code_path("bk_list.json"), "w") as f:
        f.write(json.dumps(dict(code=block_list)))

def get_stock_codes2():
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

