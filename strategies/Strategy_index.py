from easyquant import StrategyTemplate
from threading import Thread, current_thread, Lock
import json
import redis
import time
import pymongo
import pandas as pd
import talib

class calcStrategy(Thread):
    def __init__(self, code, data, log, chkv, mdb):
        Thread.__init__(self)
        self._data = data
        self._code = code
        self._log = log
        self._chkv = chkv
        # log.info("code=%s, code=%s"%(code, code[2:]))
        data=mdb['index_day'].find({'code':code[2:]})
        self._df = pd.DataFrame(list(data))


        # self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def run(self):
        # pass
        # time.sleep(1)
        # print (type(self._data))
        # self.redis.hmset(self._code, self._data)

        chgValue = (self._data['now'] - self._data['close'])
        # downPct = (self._data['high'] - self._data['now']) * 100 / self._data['now']
        # chkVPct =  ( self._data['now'] - self._chkv  ) * 100 / self._chkv
        pct = chgValue * 100 / self._data['close']
        hp = self._data['high'] - self._data['close']
        lp = self._data['low'] - self._data['close']
        cp= self._data['now'] - self._data['close']
        cs = pd.Series({'close':self._data['close']})
        df2 = self._df.append(cs, ignore_index=True) 
        idx = self._df.index.values.size - 1
        ma20 = talib.MA(self._df.close,20)
        ma202 = talib.MA(df2.close,20)
        # print ("code=%s now=%6.2f pct=%6.2f hl=%6.2f" % ( self._code, self._data['now'], pct, downPct))
        # self._log.info("code=%s now=%6.2f pct=%6.2f pctv2=%6.2f" % ( self._code, self._data['now'], pct, chkVPct))
        #if pct > 0.2 or pct < -0.2 :
        # self._log.info("code=%s now=%6.2f pct=%6.2f cp=%6.2f hp=%6.2f  lp=%6.2f " % (self._code, self._data['now'], pct, cp, hp, lp))
        self._log.info("code=%s now=%6.2f pct=%6.2f cp=%6.2f hp=%6.2f  lp=%6.2f " % (self._code, self._data['now'], pct, ma20[idx], ma202[idx], ma202[idx+1]))

class Strategy(StrategyTemplate):
    name = 'index'

    def __init__(self, user, log_handler, main_engine, mdb):
        StrategyTemplate.__init__(self, user, log_handler, main_engine, mdb)
        self.log.info('init event index.')
        self.chks=[]
        self.mdb = mdb
        config_name = './config/chklist.json'
        with open(config_name, 'r') as f:
            data = json.load(f)
            # print data
            for d in data['chk-index']:
                self.chks.append((d['c'], d['p']))
                # print d['c']

    def strategy(self, event):
        self.log.info('\n\nStrategy index event')
        # chklist = ['002617','600549','300275','000615']
        # print  (type(event.data))
        threads = []
        # [calcStrategy(l) for i in range(5)]
        #for td in event.data:
        #    self.log.info(td)

        for td in self.chks:
            if td[0] in event.data:
                threads.append(calcStrategy(td[0], event.data[td[0]], self.log, td[1], self.mdb))
            # else:
            #     self.log.info("\n\nnot in data:" + td[0])

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

