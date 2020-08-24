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
from custom.util import new_df, tdx_func

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
executor = ProcessPoolExecutor(max_workers=cpu_count() * 4)
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
    data_day = mongo.get_stock_day(code=code, st_start="2020-01-01")
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
    # print("code=%s, price=%.2f" % (code, now_price))
    high_price = data['high']
    ##TODO 绝对条件１
    ## 止损卖出
    # if now_price < hold_price / 1.05:
    #     log.info("code=%s now=%6.2f solding..." % (code, now_price))
    ## 止赢回落 %5，卖出
    # if now_price > hold_price * 1.02 and now_price < high_price / 1.03:
    #     log.info("code=%s now=%6.2f solding..." % (code, now_price))
        # 卖出

    # now_vol = data['volume']
    # last_time = pd.to_datetime(data['datetime'][0:10])
    # print("code=%s, data=%s" % (self.code, self._data['datetime']))
    df_day = data_buf_day[code]
    # print(len(df_day))
    # print("code=%s, nums=%d" % (code, len(df_day)))
    # print("code=%s, data=%s" % (data['code'], data['datetime']))
    # print(data)
    df_day = new_df(df_day, data, now_price)
    # print(df_day.tail())
    chk_flg = tdx_func(df_day)
    # df_day.loc[last_time]=[0 for x in range(len(df_day.columns))]
    # df_day.loc[(last_time,code),'open'] = data['open']
    # df_day.loc[(last_time,code),'high']= data['high']
    # df_day.loc[(last_time,code),'low'] = data['low']
    # df_day.loc[(last_time,code),'close'] = now_price
    # df_day.loc[(last_time,code),'vol'] = data['volume']
    # df_day.loc[(last_time,code),'amount'] = data['amount']
    # df=pd.concat([MA(df_day.close, x) for x in (5,10,20,30,60,90,120,250,500,750,1000,1500,2000,2500,) ], axis = 1)[-1:]
    # df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm500', u'm750', u'm1000', u'm1500', u'm2000', u'm2500']
    # df=pd.concat([MA(df_day.close, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
    # df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

    # df_v=pd.concat([MA(df_day.vol, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
    # df_v.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

    # df_a=pd.concat([MA(df_day.amount, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)
    # df_a.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

    # self.log.info("data=%s, m5=%6.2f" % (self.code, df.m5.iloc[-1]))
    # self.upd_min(5)
    # self.log.info()
    # if now_vol > df_v.m5.iloc[-1]:
    # self.log.info("code=%s now=%6.2f pct=%6.2f m5=%6.2f, now_vol=%10f, m5v=%10f" % (self.code, now_price, self._data['chg_pct'], df.m5.iloc[-1], now_vol, df_v.m5.iloc[-1]))
    # if toptop_calc(df_day):
    # if now_price < df.m5.iloc[-1]:
    ## 低于５日线，卖出
    # print(chk_flg[-1])
    if chk_flg[-1]:
        # log.info("code=%s now=%6.2f DHM" % (code, now_price))
        # 卖出
        print("calc code=%s now=%6.2f DHM" % (code, now_price))

class Strategy:
    name = 'calc-stock-dhm'  ### day

    def __init__(self):
        # self.log = log_handler
        # self.log.info('init event:%s'% self.name)
        print("init...")
        
        # self.df_positions = mongo.get_positions()
        
        # self.easymq = EasyMq()
        # self.easymq.init_receive(exchange="stockcn")
        # self.easymq.callback = self.callback
        
        # start_time = time.time()
        start_t = datetime.datetime.now()
        print("read data-begin-time:", start_t)

        task_list = []
        codelist = QA.QA_fetch_stock_list_adv()
        print("read data...")
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
        print(end_t, 'read data-spent:{}'.format((end_t - start_t)))

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
        # self.log.info('Strategy =%s, easymq started' % self.name)
        # self.started = True
        # self.easymq.start()
        # self.log.info('Strategy =%s, start calc...')
        task_list = []
        datas = fetch_quotation_data()
        for stcode in datas:
            data = datas[stcode]
        # for stcode in event.data:
            # stdata= event.data[stcode]
            # self.log.info("data=%s, data=%s" % (stcode, stdata))
            # self.easymq.pub(json.dumps(stdata, cls=CJsonEncoder), stcode)
            # aa = json.dumps(stdata)
            # self.log.info("code=%s, data=%s" % (stcode, aa))
            jsdata = json.dumps(data)
            # self.easymq.pub(json.dumps(stdata), stcode)
            # rtn=self.data_util.day_summary(data=stdata, rtn=rtn)
            # print(stcode)
            task_list.append(executor.submit(do_main_work, stcode, data,))
            # print(jsdata)
        # data = json.loads(data)
        # code =data['code']
        # t.start()
        # executor.submit(do_main_work, code, data, self.log, self.df_positions.loc[code])
        for task in as_completed(task_list):
            # result = task.result()
            pass

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
