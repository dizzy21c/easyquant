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

class Strategy(StrategyTemplate):
    name = 'save-data-disp'
    idx = 0
    EventType = 'data-sina'
    config_name = './config/worker_list.json'

    def __init__(self, user, log_handler, main_engine):
        StrategyTemplate.__init__(self, user, log_handler, main_engine)
        self.log.info('init event:%s'% self.name)
        # self.redis = RedisIo()
        self.data_util = DataUtil()
        
        self.easymq = EasyMq()
        self.easymq.init_pub(exchange="stockcn")

    def strategy(self, event):
        if event.event_type != self.EventType:
            return

        self.log.info('Strategy =%s, event_type=%s' %(self.name, event.event_type))
        threads = []
        rtn = {}
        # print(datetime.datetime.now())
        for stcode in event.data:
            stdata= event.data[stcode]
            # self.log.info("data=%s" % stcode)
            # self.easymq.pub(json.dumps(stdata, cls=CJsonEncoder), stcode)
            self.easymq.pub(json.dumps(stdata), stcode)
            rtn=self.data_util.day_summary(data=stdata,rtn=rtn)
            # threads.append(calcStrategy(stcode, stdata, self.log, self.idx, self.easymq))
        self.log.info(rtn)

        # for c in threads:
        #     c.start()

class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        # elif isinstance(obj, date):
        #     return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)