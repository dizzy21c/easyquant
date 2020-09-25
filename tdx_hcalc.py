# from easyquant import StrategyTemplate
# from easyquant import RedisIo
from easyquant import DataUtil
from threading import Thread, current_thread, Lock
import QUANTAXIS as QA
import json
import datetime

# import redis
import time
# import datetime
# from datetime import datetime, date
import pandas as pd

# import pymongo
import pika
# from QUANTAXIS.QAFetch import QATdx as tdx
# from easyquant import DefaultLogHandler
# from custom import tdx_func
from tdx.func.tdx_func import new_df, tdx_hm, tdx_dhmcl, tdx_tpcqpz

# from easyquant import EasyMq
from easyquant import MongoIo
from easyquant import EasyTime
from multiprocessing import Process, Pool, cpu_count, Manager
# from easyquant.indicator.base import *
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor,as_completed
#from pyalgotrade.strategy import position
# from custom.sinadataengine import SinaEngine
import easyquotation

# calc_thread_dict = Manager().dict()
data_buf_day = Manager().dict()
# data_buf_5min = Manager().dict()
# data_buf_5min_0 = Manager().dict()
# mongo = MongoIo()
easytime=EasyTime()
executor = ProcessPoolExecutor(max_workers=cpu_count())
executor2 = ThreadPoolExecutor(max_workers=cpu_count() * 4)

# class DataSinaEngine(SinaEngine):
#     EventType = 'data-sina'
#     PushInterval = 10
#     config = "stock_list"

def fetch_quotation_data(config="stock_list"):
    source = easyquotation.use("sina")
    config_name = './config/%s.json' % config
    with open(config_name, 'r') as f:
        data = json.load(f)
        out = source.stocks(data['code'])
        # print (out)
        while len(out) == 0:
            out = source.stocks(data['code'])
        # print (out)
        return out
        
# dataSrc = DataSinaEngine()

def do_init_data_buf(code):
    # freq = 5
    # 进程必须在里面, 线程可以在外部
    # mc = MongoIo()
    # mongo = MongoIo()
    # if idx == 0:
    mongo = MongoIo()
    data_day = mongo.get_stock_day(code=code, st_start="2019-01-01")
        # data_min = mc.get_stock_min_realtime(code=code, freq=freq)
    # else:
    #     data_day = mongo.get_index_day(code=code)
        # data_min = mc.get_index_min_realtime(code=code)
    data_buf_day[code] = data_day
    # data_buf_5min[code] = data_min
    # print("do-init data end, code=%s, data-buf size=%d " % (code, len(data_day)))
    
def do_main_work(code, data):
    # hold_price = positions['price']
    now_price = data['now']
    try:
        df_day = data_buf_day[code]
        df_day = new_df(df_day, data, now_price)
        # print(df_day.tail())
        chk_flg, _ = tdx_dhmcl(df_day)
        chk_flg2, _ = tdx_hm(df_day)
        chk_flg3, _ = tdx_tpcqpz(df_day)
        if chk_flg[-1]:
            print("calc code=%s now=%6.2f DHM" % (code, now_price))

        if chk_flg2[-1]:
            print("calc code=%s now=%6.2f HM" % (code, now_price))

        if chk_flg3[-1]:
            print("calc code=%s now=%6.2f TPCQPZ" % (code, now_price))
    except:
        print("error code=%s, df-day-len=%d data-len=%d" % (code, len(df_day), len(data)) )
        return

class Strategy:
    name = 'calc-stock-dhm'  ### day

    def __init__(self):
        # self.log = log_handler
        # self.log.info('init event:%s'% self.name)
        # print("init...")
        
        # self.df_positions = mongo.get_positions()
        
        # self.easymq = EasyMq()
        # self.easymq.init_receive(exchange="stockcn")
        # self.easymq.callback = self.callback
        
        # start_time = time.time()
        start_t = datetime.datetime.now()
        print("read db data-begin-time:", start_t)

        task_list = []
        codelist = QA.QA_fetch_stock_list_adv()
        # print("read data...")
        # idx = 1
        for code in codelist.index:
            task_list.append(executor.submit(do_init_data_buf, code))
            # self.easymq.add_sub_key(routing_key=code)
            # print("read %s..." % code)
            # idx = idx + 1
            # if idx > 10:
            #     break
        
        for task in as_completed(task_list):
            # result = task.result()
            pass
        
        end_t = datetime.datetime.now()
        print(end_t, 'read db data-spent:{}'.format((end_t - start_t)))

        # self.log.info('init event end:%s, user-time=%d' % (self.name, time.time() - start_time))
        
        ## init message queue
        # self.started=False
        # self.easymq = EasyMq()
        # self.easymq.init_receive(exchange="stockcn")
        # self.easymq.callback = self.callback
        # with open(self.config_name, 'r') as f:
        #     data = json.load(f)
        #     for d in data['code']:
        #         if len(d) > 6:
        #             d = d[len(d)-6:len(d)]
        #         self.easymq.add_sub_key(routing_key=d)
                # self.code_list.append(d)
                # 
                # pool.apply_async(do_init_data_buf, args=(d, self.idx, self.data_type))
        # self.easymq.callback = mycallback
        # self.easymq.start()
    def start(self):
        while True:
            print("*** loop calc begin ***")
            self.do_calc()

    def do_calc(self):
        # self.log.info('Strategy =%s, easymq started' % self.name)
        # self.started = True
        # self.easymq.start()
        # self.log.info('Strategy =%s, start calc...')
        task_list = []
        start_t = datetime.datetime.now()
        print("read web data-begin-time:", start_t)
        
        datas = fetch_quotation_data()
        end_t = datetime.datetime.now()
        print(end_t, 'read web data-spent:{}'.format((end_t - start_t)))
        
        start_t = datetime.datetime.now()
        print("do-task1-begin-time:", start_t)
        for stcode in datas:
            data = datas[stcode]
        # for stcode in event.data:
            # stdata= event.data[stcode]
            # self.log.info("data=%s, data=%s" % (stcode, stdata))
            # self.easymq.pub(json.dumps(stdata, cls=CJsonEncoder), stcode)
            # aa = json.dumps(stdata)
            # self.log.info("code=%s, data=%s" % (stcode, aa))
            # jsdata = json.dumps(data)
            # self.easymq.pub(json.dumps(stdata), stcode)
            # rtn=self.data_util.day_summary(data=stdata, rtn=rtn)
            # print(stcode)
            task_list.append(executor.submit(do_main_work, stcode, data,))
            # print(jsdata)
        end_t = datetime.datetime.now()
        print(end_t, 'do-task1-spent:{}'.format((end_t - start_t)))

        # data = json.loads(data)
        # code =data['code']
        # t.start()
        # executor.submit(do_main_work, code, data, self.log, self.df_positions.loc[code])
        start_t = datetime.datetime.now()
        print("do-task2-begin-time:", start_t)
        
        for task in as_completed(task_list):
            result = task.result()
            # pass
        end_t = datetime.datetime.now()
        print(end_t, 'do-task2-spent:{}'.format((end_t - start_t)))

if __name__ == "__main__":
    start_t = datetime.datetime.now()
    print("begin-time:", start_t)

    log_type = 'file'#'stdout' if log_type_choose == '1' else 'file'
    # log_name = Strategy.name
    # log_filepath = 'logs/%s.txt' % Strategy.name
    # log_handler = DefaultLogHandler(name='calc-data', log_type=log_type, filepath=log_filepath)
    
    s = Strategy()
    s.start()
    end_t = datetime.datetime.now()
    print(end_t, 'spent:{}'.format((end_t - start_t)))
