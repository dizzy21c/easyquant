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
    def __init__(self, code, data, log, redis, hdata):
        Thread.__init__(self)
        self.data = data
        self.code = code
        self.log = log
        # self._chkv = chkv[1]
        # self.hdata=chkv[2]
        # self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.redis = redis
        self.hdata = hdata
        self.lasttm = ""
    def redis_push_day(self, data):
        df = self.redis.get_day_df(self.code)
        ldata = data['date']
        if list(df['date'])[-1] == ldata:
            return

        self.redis.push_day_data(self.code, data)
        
    def redis_push(self, data):
        ct=time.strftime("%H:%M:%S", time.localtime()) 
        if self.lasttm == data['time']:
            return
        self.lasttm = data['time']

        #dt=data['time']
        if ct < "09:25:00":
            return

        if ct > "11:30:10" and ct < "12:59:59":
            return

        if ct > "15:00:10":
            return

        self.redis.push_cur_data(self.code, data)

    def run(self):
        # pass
        # time.sleep(1)
        #print (type(self._data))
        #print (self._data)
        # self.redis.hmset(self._code, self._data)
        # self.redis_push_day(self.data)

        # chgValue = (self.data['now'] - self.data['close'])
        # downPct = (self._data['high'] - self._data['now']) * 100 / self._data['now']
        # upPct = (self._data['high'] - self._data['now']) * 100 / self._data['now']
        # chkVPct =  ( self.data['now'] - self._chkv  ) * 100 / self._chkv
        # pct = chgValue * 100 / self.data['close']
        # print ("code=%s now=%6.2f pct=%6.2f hl=%6.2f" % ( self._code, self._data['now'], pct, downPct))

        if self.code in self.hdata.keys():
            chgValue = (self.data['now'] - self.data['close'])
            pct = chgValue * 100 / self.data['close']
            if pct > 3 or (pct < 0 and pct > -12) :
            # self.log.info("code=%s now=%6.2f pct=%6.2f h=%6.2f l=%6.2f" % ( self.code, self.data['now'], pct, self.data['high'], self.data['low']))
                self.log.info("code=%s now=%6.2f pct=%6.2f h=%6.2f l=%6.2f" % ( self.code, self.data['now'], pct, self.data['high'], self.data['low']))
            #self.log.info("code=%s now=%6.2f pct=%6.2f h=%6.2f l=%6.2f" % ( self.code, self.data['now'], pct, self.data['high'], self.data['low']))
          #self._log.info("code=%s now=%6.2f pct=%6.2f pctv2=%6.2f" % ( self._code, self._data['now'], pct, chkVPct))
        #self._log.info("  end." )

class Strategy(StrategyTemplate):
    name = 'save data'

    def __init__(self, user, log_handler, main_engine):
        StrategyTemplate.__init__(self, user, log_handler, main_engine)
        self.log.info('init event:%s'% self.name)
        self.hdata={}
        # self.chks=[]
        config_name = './config/worker_list.json'
        self.rio = RedisIo('./redis.conf')
        self.data_util = DataUtil()
        #self.redis = redis.Redis(host='localhost', port=6379, db=0)
        with open(config_name, 'r') as f:
            data = json.load(f)
            # print data
            for d in data['chk']:
                # self.log.info(d)
                #rdata=self._db.lrange(d['c'][2:],0,-1)
                #clist=[json.loads(v.decode()) for v in rdata]
                rlist=self.rio.get_day_c(d['c'])
                self.hdata[d['c']] = rlist

                # print d['c']

    def strategy(self, event):
        if event.event_type != 'data-sina':
            return

        self.log.info('\nStrategy =%s, event_type=%s' %(self.name, event.event_type))
        
        # chklist = ['002617','600549','300275','000615']
        # print  (type(event.data))
        threads = []
        # [calcStrategy(l) for i in range(5)]
        rtn = {}
        for stcode in event.data:
            # self.log.info(stcode)
            # self.log.info(event.data)
            stdata= event.data[stcode]
            # self.log.info(stdata)
            rtn=self.data_util.day_summary(data=stdata,rtn=rtn)
            threads.append(calcStrategy(stcode, stdata, self.log, self.rio, self.hdata))
        # for td in self.chks:
        #     if td[0] in event.data:
        #         threads.append(calcStrategy(td[0], event.data[td[0]], self.log, td, self.rio))
            # else:
            #     self.log.info("\n\nnot in data:" + td[0])
        #code print
        #for td in event.data:
        #   self.log.info(td) 
        # for d in event.data:
        #     threads.append(calcStrategy(d, event.data[d], self.log))

        self.log.info(rtn)

        for c in threads:
            c.start()

            # chgValue = (event.data[d]['now'] - event.data[d]['close'])
            # self.log.info( "code=%s pct=%6.2f now=%6.2f" % (d, ( chgValue * 100/ event.data[d]['now']), event.data[d]['now']))

        

