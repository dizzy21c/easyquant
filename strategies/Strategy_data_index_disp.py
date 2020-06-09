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
        self.easymq.init_pub(exchange="stockcn.idx")

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

        

