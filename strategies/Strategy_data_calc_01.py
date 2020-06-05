from easyquant import StrategyTemplate
# from easyquant import RedisIo
from easyquant import DataUtil
from threading import Thread, current_thread, Lock
import json
# import redis
import time
# import datetime
from datetime import datetime, date

# import pymongo
# import pandas as pd
# import talib
import pika

from easyquant import EasyMq
from multiprocessing import Pool, cpu_count

# class calcStrategy(Thread):
#     def __init__(self, code, data, log, idx, easymq):
#         Thread.__init__(self)
#         self._data = data
#         self.code = code
#         self.log = log
#         self.easymq = easymq
#         # self.redis = redis
#         self.idx = idx
#         # self.hdata = hdata
#         # self.lasttm = ""

#     def run(self):
#         # self.easymq.pub(text=self.code, routing_key = self.code)
#         # self.log.info("data=%s" % self._data)
#         chgValue = (self._data['now'] - self._data['close'])
#         # downPct = (self._data['high'] - self._data['now']) * 100 / self._data['now']
#         # upPct = (self._data['high'] - self._data['now']) * 100 / self._data['now']
#         # chkVPct =  ( self._data['now'] - self._chkv  ) * 100 / self._chkv
#         pct = chgValue * 100 / self._data['close']
#         # print ("code=%s now=%6.2f pct=%6.2f hl=%6.2f" % ( self._code, self._data['now'], pct, downPct))
#         # if pct > 3 or (pct < 0 and pct > -12) :
#         self.log.info("code=%s now=%6.2f pct=%6.2f h=%6.2f l=%6.2f" % ( self.code, self._data['now'], pct, self._data['high'], self._data['low']))
#         #   self._log.info("code=%s now=%6.2f pct=%6.2f h=%6.2f l=%6.2f" % ( self._code, self._data['now'], pct, self._data['high'], self._data['low']))
        
#         # if self.code == "000004" or self.code == "000001":
#         #     self.log.info("data=%s" % self.data['name'])
#         # self.log.info("code=%s, time=%s" % (self.code, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
#         # self.redis.set_cur_data(self.code, self.data, idx = 0)
#         # if self.data['open'] <= 0:
#         #     return
#         # self.redis.push_day_data(self.code, self.data, idx = 0)
#         # # self.redis.push_cur_data(self.code, self.data, idx = 0)
        
class Strategy(StrategyTemplate):
    name = 'save-data-calc-01'
    idx = 0
    EventType = 'data-sina'
    config_name = './config/stock2_list.json'

    def __init__(self, user, log_handler, main_engine):
        StrategyTemplate.__init__(self, user, log_handler, main_engine)
        self.log.info('init event:%s'% self.name)
        # self.redis = RedisIo()
        # self.data_util = DataUtil()
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
        # if event.event_type != self.EventType:
        #     return

        # self.log.info('Strategy =%s, event_type=%s' %(self.name, event.event_type))
        # threads = []
        # rtn = {}
        # # print(datetime.datetime.now())
        # for stcode in event.data:
        #     stdata= event.data[stcode]
        #     # self.log.info("data=%s" % stcode)
        #     # self.easymq.pub(json.dumps(stdata, cls=CJsonEncoder), stcode)
        #     self.easymq.pub(json.dumps(stdata), stcode)
        #     # rtn=self.data_util.day_summary(data=stdata,rtn=rtn)
        #     # threads.append(calcStrategy(stcode, stdata, self.log, self.idx, self.easymq))
        # self.log.info(rtn)

        # # for c in threads:
        # #     c.start()
        
    def callback(self, a, b, c, data):
        data = json.loads(data)
        # self.log.info("data111=%s" % data['code'])
