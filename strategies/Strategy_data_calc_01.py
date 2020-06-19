from easyquant import StrategyTemplate
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
import talib as tdx
import pika

from easyquant import EasyMq
from easyquant import MongoIo
from multiprocessing import Process, Pool, cpu_count, Manager


# calc_thread_dict = Manager().dict()
data_buf_day = Manager().dict()
data_buf_15min = Manager().dict()
data_buf_15min_0 = Manager().dict()
# mongo = MongoIo()

def do_init_data_buf(code, idx):
    mongo=MongoIo()
    if idx == 0:
        data_day = mongo.get_stock_day(code=code)
        data_15min = mongo.get_stock_min(code=code)
    else:
        data_day = mongo.get_index_day(code=code)
        data_15min = mongo.get_index_min(code=code)

    ## TODO fuquan 
    
    data_buf_day[code] = data_day
    data_buf_15min[code] = data_15min
    # print("do-init data end, code=%s, data-buf size=%d " % (code, len(data_buf_day)))
    


class calcStrategy(Thread):
    def __init__(self, code, data, log, idx):
        Thread.__init__(self)
        self._data = data
        self.code = code
        self.log = log
        # self.redis = redis
        self.idx = idx
        # self.last_time = None
        # self.working = False
    
    # def set_data(self, code, data, idx):
    #     Thread.__init__(self)
    #     self._data = data
    #     self.code = code
    #     self.log = log
    #     # self.redis = redis

    def run(self):
        # if self.working:
        #     return
        
        # self.working = True
        now_price = self._data['now']
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
        # df=pd.concat([tdx.MA(df_day.close, x) for x in (5,10,20,30,60,90,120,250,500,750,1000,1500,2000,2500,) ], axis = 1)[-1:]
        # df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm500', u'm750', u'm1000', u'm1500', u'm2000', u'm2500']
        df=pd.concat([tdx.MA(df_day.close, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
        df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

        df_v=pd.concat([tdx.MA(df_day.vol, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
        df_v.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

        df_a=pd.concat([tdx.MA(df_day.amount, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
        df_a.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

        # self.log.info("data=%s, m5=%6.2f" % (self.code, df.m5.iloc[-1]))

        # self.log.info()
        # if now_vol > df_v.m5.iloc[-1]:
        # self.log.info("code=%s now=%6.2f pct=%6.2f m5=%6.2f, now_vol=%10f, m5v=%10f" % (self.code, now_price, self._data['chg_pct'], df.m5.iloc[-1], now_vol, df_v.m5.iloc[-1]))
        self.log.info("code=%s now=%6.2f pct=%6.2f m5=%6.2f, high=%6.2f, low=%6.2f" % (self.code, now_price, self._data['chg_pct'], df.m5.iloc[-1], self._data['high'], self._data['low']))


        # self.working = False
class Strategy(StrategyTemplate):
    name = 'save-data-calc-01'  ### day
    idx = 0
    EventType = 'data-sina'
    config_name = './config/stock2_list.json'

    def __init__(self, user, log_handler, main_engine):
        StrategyTemplate.__init__(self, user, log_handler, main_engine)
        self.log.info('init event:%s'% self.name)
        # self.redis = RedisIo()
        # self.data_util = DataUtil()
        # self.code_list = []
        self.idx=0
        self.calc_thread_dict = {}
        # init data
        start_time = time.time()
        pool = Pool(cpu_count())
        with open(self.config_name, 'r') as f:
            data = json.load(f)
            for d in data['code']:
                if len(d) > 6:
                    d = d[len(d)-6:len(d)]
                # self.code_list.append(d)
                pool.apply_async(do_init_data_buf, args=(d, 0))
                # self.calc_thread_dict[d] = calcStrategy(data['code'], self.log)
                
                
        pool.close()
        pool.join()
        pool.terminate()
        self.log.info('init event end:%s, user-time=%d' % (self.name, time.time() - start_time))
        
        ## init message queue
        self.started=False
        self.easymq = EasyMq()
        self.easymq.init_receive(exchange="stockcn")
        self.easymq.callback = self.callback
        with open(self.config_name, 'r') as f:
            data = json.load(f)
            for d in data['code']:
                if len(d) > 6:
                    d = d[len(d)-6:len(d)]
                self.easymq.add_sub_key(routing_key=d)
                # self.code_list.append(d)
                # 
                # pool.apply_async(do_init_data_buf, args=(d, self.idx, self.data_type))
        # self.easymq.callback = mycallback
        # self.easymq.start()


    def strategy(self, event):
        if self.started:
            return
        
        self.started = True
        self.easymq.start()
        
    def callback(self, a, b, c, data):
        data = json.loads(data)
        # self.log.info("data111=%s" % data['code'])
        t = calcStrategy(data['code'], data, self.log, self.idx)
        t.start()
