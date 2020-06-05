from easyquant import StrategyTemplate
# from easyquant import RedisIo
# from easyquant import DataUtil
from threading import Thread, current_thread, Lock
import json
# import redis
import time
# import pymongo
# import pandas as pd
# import talib
import pika
from easyquant import EasyMq

class calcStrategy(Thread):
    def __init__(self, code, data, log, idx):
        Thread.__init__(self)
        self.data = data
        self.code = code
        self.log = log
        # self.redis = redis
        self.idx = idx

    def run(self):
        cc=self.data['now']
        chgValue = (self.data['now'] - self.data['close'])
        # downPct = (self._data['high'] - self._data['now']) * 100 / self._data['now']
        # chkVPct =  ( self._data['now'] - self._chkv  ) * 100 / self._chkv
        pct = chgValue * 100 / self.data['close']
        hp = self.data['high'] - self.data['close']
        lp = self.data['low'] - self.data['close']
        cp= self.data['now'] - self.data['close']
        self.log.info("code=%s now=%6.2f pct=%6.2f cp=%6.2f hp=%6.2f  lp=%6.2f " % (self.code, self.data['now'], pct, cp, hp, lp))

        # self.log.info("data=%s" % self.data)
        # if self.code == "000004" or self.code == "000001":
        #     self.log.info("data=%s" % self.data['name'])
        # self.log.info("code=%s" % self.code)
        # if self.data['open'] <= 0:
        #     return
        # self.redis.set_cur_data(self.code, self.data, idx = 1)
        # self.redis.push_day_data(self.code, self.data, idx = self.idx)
        # self.redis.push_cur_data(self.code, self.data, idx = self.idx)

class Strategy(StrategyTemplate):
    name = 'save-index-data-disp'
    idx = 1
    # event_type = "data-sina"
    EventType = 'index-sina'

    def __init__(self, user, log_handler, main_engine):
        StrategyTemplate.__init__(self, user, log_handler, main_engine)
        self.log.info('init event:%s'% self.name)
        # self.redis = RedisIo()
        # self.data_util = DataUtil()
        self.easymq = EasyMq()
        self.easymq.init_pub(exchange="stockcn")

    def strategy(self, event):
        if event.event_type != self.EventType:
            return

        self.log.info('Strategy =%s, event_type=%s' %(self.name, event.event_type))
        
        threads = []
        # rtn = {}
        for stcode in event.data:
            stdata= event.data[stcode]
            self.easymq.pub(json.dumps(stdata), stcode)
            # rtn=self.data_util.day_summary(data=stdata,rtn=rtn)
            # threads.append(calcStrategy(stcode, stdata, self.log, self.idx))

        # for c in threads:
        #     c.start()

        

