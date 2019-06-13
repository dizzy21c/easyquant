from easyquant import StrategyTemplate
from easyquant.indicator.udf_formula import *
from easyquant import DataUtil
from easyquant import DefaultLogHandler
from easyquant import RedisIo
from threading import Thread, current_thread, Lock, Event
from multiprocessing import Process, Pool, cpu_count, Manager
import json
import redis
import time
#import pymongo
# from pandas import Series
# import pandas as pd
# import numpy as np
# import talib
redis=RedisIo()
data_buf = Manager().dict()
_logname="do-worker"
_log_type = 'file'#'stdout' if log_type_choose == '1' else 'file'
_log_filepath = 'logs/%s.txt' % _logname #input('请输入 log 文件记录路径\n: ') if log_type == 'file' else ''
log_handler = DefaultLogHandler(name=_logname, log_type=_log_type, filepath=_log_filepath)


def do_init_data_buf(code, idx):
    data_df = redis.get_day_df(code, idx=idx)
    data_buf[code] = data_df
    # print("do-init data data-buf size=%d " % len(data_buf))
    
    

def do_calc(code, idx):
    # print("data-buf size=%d " % len(data_bufo))
    sdata = redis.get_cur_data(code, idx = idx)
    data_df = data_buf[code]

    # print("data-buf size=%d " % len(st.code_list))
    # d = redis.get_last_date(code, idx=idx)
    # redis.get_data_value
    
    # data_df = redis.get_day_df(code, idx=idx)
    data_df = data_buf[code]
    # print("data-len=%d" % len(data_df))
    
    baseFlg, _ = udf_base_check(data_df)
    
    Flg, out = udf_dapan_risk(data_df)
    if baseFlg and Flg:
        log_handler.info(" data risk => code=%s , value= %s " %  (code, out))

    # if udf_hangqing_start(data_df):
    #     log_handler.info(" data market start=>code=%s" % code )

    # if udf_niu_check(data_df):
    #     log_handler.info(" data niu-check => code=%s" % code )



class Strategy(StrategyTemplate):
    name = 'data-worker'
    EventType = 'worker'
    config_name = './config/stock_list.json'
    idx=0

    def __init__(self, user, log_handler, main_engine):
        StrategyTemplate.__init__(self, user, log_handler, main_engine)
        start_time = time.time()
        self.log.info('init event:%s' % (self.name))
        # self.hdata={}
        self.threads = []
        # start_date = '2018-01-01'
        self.rio=RedisIo('redis.conf')
        self.data_util = DataUtil()
        self.code_list = []
        # self.pool = Pool(10)
        pool = Pool(cpu_count())
        self.is_working = False
        with open(self.config_name, 'r') as f:
            data = json.load(f)
            for d in data['code']:
                self.code_list.append(d)
                
                pool.apply_async(do_init_data_buf, args=(d, self.idx))
        #         # data_df = self.rio.get_day_df(d, idx=self.idx)
        #         # data_map = data_util.df2series(data_df)
                # self.hdata[d] = data_map

        #     for t in self.threads:
        #         # t.setDaemon(True)
        #         t.start()

            # for t in self.threads:
            #     t.join()
        pool.close()
        pool.join()
        pool.terminate()
        self.log.info('init event end:%s, user-time=%d' % (self.name, time.time() - start_time))

    def loading(self, code, idx):
        data_df = self.rio.get_day_df(code, idx=self.idx)
        data_map = self.data_util.df2series(data_df)
        # self.hdata[code] = data_map

    def strategy(self, event):
        # self.log.info('\nStrategy =%s, event_type=%s' %(self.name, event.event_type))
        if self.is_working:
            return
        if event.event_type != self.EventType:
            return
        self.log.info('Strategy =%s, event_type=%s' %(self.name, event.event_type))
        pool = Pool(cpu_count())
        self.is_working = True

        for stcode in self.code_list:
            pool.apply_async(do_calc, args=(stcode, self.idx))

        # i = 0
        # stcode = []
        # code_len = len(self.code_list)
        # while i < code_len:
        #     stcode.append(self.code_list[i])
        #     if i % 10 == 0 or i == code_len - 1:
        #         pool.apply_async(do_calc, args=(stcode, self.idx, self.pt, self.qd))
        #         stcode = []
        #     i += 1
        pool.close()
        pool.join()
        pool.terminate()
        self.is_working = False
        self.log.info("do-working-end name=%s" % self.name)