# coding:utf8
import json
import os
import re
import xlrd
import requests
from easyquant import QATdx as tdx
from easyquant.indicator.udf_formula import *
from easyquant import RedisIo
from easyquant import MongoIo
from multiprocessing import Process, Pool, cpu_count, Manager
import click
from threading import Thread, current_thread, Lock

STOCK_CODE_PATH = "config/stock_codes.conf"

class TopTopCalcThread(Thread):
    def __init__(self, code, idx):
        Thread.__init__(self)
        self.code = code
        self.idx = idx

    def run(self):
        do_init_data_buf(self.code, self.idx)


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
    codes_df=codes_df[~codes_df.name.str.contains('ST')]

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

def do_calc_top_data(code, last_day):
    # print("do-calc")
    data_df = redis.get_day_df(code, idx=0)
    C = data_df.close
    if udf_top_last(C, M = last_day, N = 30):
        top_codes.append(code)

def do_calc_2top(code, last_day):
    # print("calc_toptop_codes-cod=%s" % code )
    mongo = MongoIo()
    # last_day = "2020-06-30"
    data = mongo.get_stock_day(code, st_start="2020-03-01", st_end=last_day)
    if len(data) < 30:
        return
    # print("code=%s, len=%d, lastday=%s" % (code, len(data), data.iloc[-1].name))
    CLOSE = data.close
    C = data.close
    前炮 = CLOSE > REF(CLOSE, 1) * 1.099
    小阴小阳 = HHV(ABS(C - REF(C, 1)) / REF(C, 1) * 100, BARSLAST(前炮)) < 9
    时间限制 = IFAND(COUNT(前炮, 30) == 1, BARSLAST(前炮) > 5, True, False)
    后炮 = IFAND(REF(IFAND(小阴小阳, 时间限制, 1, 0), 1) , 前炮, True, False)
    if 后炮.iloc[-1]:
        top_codes.append(code)

def calc_top_codes(code_type, last_day):
    # redis=RedisIo()
    config_name = 'stock_list.json'
    # codes=[]
    pool = Pool(cpu_count())
    with open(stock_code_path(config_name), 'r') as f:
        data = json.load(f)
        for code in data['code']:
            pool.apply_async(do_calc_top_data, args=(code,last_day,))

    pool.close()
    pool.join()
    pool.terminate()
    
    codes = []
    for mc in top_codes: 
        codes.append(mc)
    with open(stock_code_path("top_list.json"), "w") as f:
        f.write(json.dumps(dict(code=codes)))


def calc_toptop_codes(_code_type, last_day):
    # redis=RedisIo()
    config_name = 'stock_list.json'
    # codes=[]
    pool = Pool(cpu_count())
    with open(stock_code_path(config_name), 'r') as f:
        data = json.load(f)
        for code in data['code']:
            # pool.apply_async(do_calc_2top, args=(code, last_day,))
            do_calc_2top(code, last_day)

    pool.close()
    pool.join()
    pool.terminate()

    codes = []
    for mc in top_codes:
        codes.append(mc)
    with open(stock_code_path("toptop_list.json"), "w") as f:
        f.write(json.dumps(dict(code=codes)))


@click.command ()
# @click.option ('--count', default=1, help = 'Number of greetings.') 
@click.option ('--last-day', default="5", help = 'Number of greetings.') 
# @click.option('--name', prompt = 'strategy name', help= 'test strategy name[data-worker]') 
@click.option('--code-type', default = "top-codes", help= 'code type[top-codes, toptop-codes]')
def main_func(code_type, last_day):
    if code_type == "top-codes":
        calc_top_codes(code_type, last_day)
    elif code_type == "toptop-codes":
        print("do toptop-codes-calc")
        calc_toptop_codes(code_type, last_day)
    else:
        get_stock_codes()

# redis=RedisIo()
# top_codes = Manager().list()
# mongo = MongoIo()
if __name__ == "__main__":
    redis=RedisIo()
    top_codes = Manager().list()
    # get_stock_codes()
    main_func()
    # calc_toptop_codes("code_type", "last_day")
    # main_func(code_type="toptop-codes")

