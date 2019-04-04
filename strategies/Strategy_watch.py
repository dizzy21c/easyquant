from easyquant import StrategyTemplate
from threading import Thread, current_thread, Lock
import json
import redis
import time
import pymongo
import pandas as pd
import talib

class calcStrategy(Thread):
    def __init__(self, code, data, log, chkv, redis):
        Thread.__init__(self)
        self._data = data
        self._code = code
        self._log = log
        self._chkv = chkv
        # self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.redis = redis

    def _redis_push(self, flg, data):
        self.redis.rpush("%s:%s"%(self._code[2:], flg), data)

    def run(self):
        # pass
        # time.sleep(1)
        # print (type(self._data))
        # self.redis.hmset(self._code, self._data)
        self._redis_push('c', self._data['now'])
        self._redis_push('o', self._data['open'])
        self._redis_push('h', self._data['high'])
        self._redis_push('l', self._data['low'])
        self._redis_push('v', self._data['volume'])

        chgValue = (self._data['now'] - self._data['close'])
        # downPct = (self._data['high'] - self._data['now']) * 100 / self._data['now']
        # upPct = (self._data['high'] - self._data['now']) * 100 / self._data['now']
        chkVPct =  ( self._data['now'] - self._chkv  ) * 100 / self._chkv
        pct = chgValue * 100 / self._data['close']
        # print ("code=%s now=%6.2f pct=%6.2f hl=%6.2f" % ( self._code, self._data['now'], pct, downPct))
        if pct > 2 or (pct < 0 and pct > -12) :
        #self._log.info("code=%s now=%6.2f pct=%6.2f h=%6.2f l=%6.2f" % ( self._code, self._data['now'], pct, self._data['high'], self._data['low']))
          self._log.info("code=%s now=%6.2f pct=%6.2f h=%6.2f l=%6.2f" % ( self._code, self._data['now'], pct, self._data['high'], self._data['low']))
          #self._log.info("code=%s now=%6.2f pct=%6.2f pctv2=%6.2f" % ( self._code, self._data['now'], pct, chkVPct))
        #self._log.info("  end." )

class Strategy(StrategyTemplate):
    name = 'test2'

    def __init__(self, user, log_handler, main_engine, db):
        StrategyTemplate.__init__(self, user, log_handler, main_engine, db)
        self.log.info('init event.')
        self.chks=[]
        config_name = './config/chklist.json'
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        with open(config_name, 'r') as f:
            data = json.load(f)
            # print data
            for d in data['chk']:
                self.chks.append((d['c'], d['p']))
                # print d['c']

    def strategy(self, event):
        self.log.info('\n\nStrategy 2 event')
        # chklist = ['002617','600549','300275','000615']
        # print  (type(event.data))
        threads = []
        # [calcStrategy(l) for i in range(5)]
        for td in self.chks:
            if td[0] in event.data:
                threads.append(calcStrategy(td[0], event.data[td[0]], self.log, td[1], self.redis))
            # else:
            #     self.log.info("\n\nnot in data:" + td[0])
        #code print
        #for td in event.data:
        #   self.log.info(td) 
        # for d in event.data:
        #     threads.append(calcStrategy(d, event.data[d], self.log))

        for c in threads:
            c.start()

            # chgValue = (event.data[d]['now'] - event.data[d]['close'])
            # self.log.info( "code=%s pct=%6.2f now=%6.2f" % (d, ( chgValue * 100/ event.data[d]['now']), event.data[d]['now']))

        # self.log.info('data: stock-code-name %s' % event.data['162411'])
        # self.log.info('check balance')
        # self.log.info(self.user.balance)
        # self.log.info('\n')

