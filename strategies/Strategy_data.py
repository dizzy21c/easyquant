from easyquant import StrategyTemplate
from easyquant import RedisIo
from easyquant import DataUtil
from threading import Thread, current_thread, Lock
import json
import redis
import time
import pymongo
import pandas as pd
import talib

class calcStrategy(Thread):
    def __init__(self, code, data, log, redis, idx):
        Thread.__init__(self)
        self.data = data
        self.code = code
        self.log = log
        self.redis = redis
        self.idx = idx
        # self.hdata = hdata
        self.lasttm = ""

    def run(self):
        self.redis.push_day_data(self.code, self.data, idx = self.idx)

class Strategy(StrategyTemplate):
    name = 'save data'
    idx = 0
    data_type = "data-sina"

    def __init__(self, user, log_handler, main_engine):
        StrategyTemplate.__init__(self, user, log_handler, main_engine)
        self.log.info('init event:%s'% self.name)
        self.rio = RedisIo('./redis.conf')
        self.data_util = DataUtil()

    def strategy(self, event):
        if event.event_type != self.data_type:
            return

        self.log.info('\nStrategy =%s, event_type=%s' %(self.name, event.event_type))
        
        threads = []
        rtn = {}
        for stcode in event.data:
            stdata= event.data[stcode]
            rtn=self.data_util.day_summary(data=stdata,rtn=rtn)
            threads.append(calcStrategy(stcode, stdata, self.log, self.rio, self.idx))

        self.log.info(rtn)

        for c in threads:
            c.start()

        

