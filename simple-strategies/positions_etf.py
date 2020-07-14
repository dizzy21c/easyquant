# from easyquant import StrategyTemplate
# from easyquant import RedisIo
from easyquant import DataUtil
from threading import Thread, current_thread, Lock
import json
# import redis
import time
# import datetime
from datetime import datetime, date
import pandas as pd

# import pymongo
import pika
# from QUANTAXIS.QAFetch import QATdx as tdx
from easyquant import DefaultLogHandler


from easyquant import EasyMq
from easyquant import MongoIo
from easyquant import EasyTime
from multiprocessing import Process, Pool, cpu_count, Manager
from easyquant.indicator.base import *
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor,as_completed
#from pyalgotrade.strategy import position


# calc_thread_dict = Manager().dict()
data_buf_day = Manager().dict()
# data_buf_5min = Manager().dict()
# data_buf_5min_0 = Manager().dict()
mongo = MongoIo()
easytime=EasyTime()
executor = ThreadPoolExecutor(max_workers=cpu_count() * 2)
def do_init_data_buf(code):
    # freq = 5
    # 进程必须在里面, 线程可以在外部
    # mc = MongoIo()
    # mongo = MongoIo()
    # if idx == 0:
    data_day = mongo.get_index_day(code=code) #, st_start="2020-05-15")
        # data_min = mc.get_stock_min_realtime(code=code, freq=freq)
    # else:
    #     data_day = mongo.get_index_day(code=code)
        # data_min = mc.get_index_min_realtime(code=code)
    ## TODO fuquan
    data_buf_day[code] = data_day
    # data_buf_5min[code] = data_min
    # print("do-init data end, code=%s, data-buf size=%d " % (code, len(data_day)))

class calcStrategy(Thread):
    def __init__(self, code, data, log, positions):
        Thread.__init__(self)
        self._data = data
        self.code = code
        self.log = log
        # self.redis = redis
        # self.idx = idx
        self.positions = positions
        # self.last_time = None
        # self.working = False
        self.price = self.positions['price']
    
    def run(self):
        
        # self.working = True
        now_price = self._data['now']
        ##TODO 绝对条件１
        if now_price < self.price / 1.05:
            pass
            # 卖出
        
        now_vol = self._data['volume']
        last_time = pd.to_datetime(self._data['datetime'][0:10])
        # print("code=%s, data=%s" % (self.code, self._data['datetime']))
        df_day = data_buf_day[self.code]
        df_day.loc[last_time]=[0 for x in range(len(df_day.columns))]
        df_day.loc[last_time,'open'] = self._data['open']
        df_day.loc[last_time,'high']= self._data['high']
        df_day.loc[last_time,'low'] = self._data['low']
        df_day.loc[last_time,'close'] = now_price
        df_day.loc[last_time,'vol'] = self._data['volume']
        df_day.loc[last_time,'amount'] = self._data['amount']
        # df=pd.concat([MA(df_day.close, x) for x in (5,10,20,30,60,90,120,250,500,750,1000,1500,2000,2500,) ], axis = 1)[-1:]
        # df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm500', u'm750', u'm1000', u'm1500', u'm2000', u'm2500']
        df=pd.concat([MA(df_day.close, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
        df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

        df_v=pd.concat([MA(df_day.vol, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
        df_v.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

        df_a=pd.concat([MA(df_day.amount, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
        df_a.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

        # self.log.info("data=%s, m5=%6.2f" % (self.code, df.m5.iloc[-1]))
        # self.upd_min(5)
        # self.log.info()
        # if now_vol > df_v.m5.iloc[-1]:
        # self.log.info("code=%s now=%6.2f pct=%6.2f m5=%6.2f, now_vol=%10f, m5v=%10f" % (self.code, now_price, self._data['chg_pct'], df.m5.iloc[-1], now_vol, df_v.m5.iloc[-1]))
        # if toptop_calc(df_day):
        if now_price < df.m5.iloc[-1]:
            chag_pct = (self._data['now'] - self._data['close']) / self._data['close'] * 100
            self.log.info("toptop code=%s now=%6.2f pct=%6.2f m5=%6.2f, high=%6.2f, low=%6.2f" % (self.code, now_price, chag_pct, df.m5.iloc[-1], self._data['high'], self._data['low']))


        # self.working = False
class Strategy:
    name = 'calc-etf'  ### day

    def __init__(self, log_handler):
        self.log = log_handler
        self.log.info('init event:%s'% self.name)
        
        self.df_positions = mongo.get_positions()
        
        self.easymq = EasyMq()
        self.easymq.init_receive(exchange="stockcn.idx")
        self.easymq.callback = self.callback
        
        start_time = time.time()
        task_list = []
        for code in self.df_positions.index:
            task_list.append(executor.submit(do_init_data_buf, code))
            self.easymq.add_sub_key(routing_key=code)
            
        for task in as_completed(task_list):
            # result = task.result()
            pass

        self.log.info('init event end:%s, user-time=%d' % (self.name, time.time() - start_time))
        
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
        self.log.info('Strategy =%s, easymq started' % self.name)
        self.started = True
        self.easymq.start()
        
    def callback(self, a, b, c, data):
        # self.log.info('Strategy =%s, start calc...' % self.name)
        data = json.loads(data)
        code =data['code']
        t = calcStrategy(code, data, self.log, self.df_positions.loc[code])
        t.start()

if __name__ == "__main__":
    log_type = 'file'#'stdout' if log_type_choose == '1' else 'file'
    # log_name = Strategy.name
    log_filepath = 'logs/%s.txt' % Strategy.name
    log_handler = DefaultLogHandler(name='calc-data', log_type=log_type, filepath=log_filepath)
    
    s = Strategy(log_handler)
    s.start()
