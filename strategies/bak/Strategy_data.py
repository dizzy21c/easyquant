from easyquant import StrategyTemplate
from threading import Thread, current_thread, Lock
from pymongo import MongoClient
import json
import redis
import time

class calcStrategy(Thread):
    def __init__(self, code, data, log, chkv):
        Thread.__init__(self)
        self._data = data
        self._code = code
        self._log = log
        self._chkv = chkv
        # self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def run(self):
        # pass
        # time.sleep(1)
        # print (type(self._data))
        # self.redis.hmset(self._code, self._data)

        chgValue = (self._data['now'] - self._data['close'])
        # downPct = (self._data['high'] - self._data['now']) * 100 / self._data['now']
        # upPct = (self._data['high'] - self._data['now']) * 100 / self._data['now']
        # chkVPct =  ( self._data['now'] - self._chkv  ) * 100 / self._chkv
        pct = -100
        if self._data['close'] > 0:
            pct = chgValue * 100 / self._data['close']
        # print ("code=%s now=%6.2f pct=%6.2f hl=%6.2f" % ( self._code, self._data['now'], pct, downPct))
        if pct > 5 or (pct < -5 and pct > -12) :
            self._log.info("code=%s now=%6.2f pct=%6.2f h=%6.2f l=%6.2f" % ( self._code, self._data['now'], pct, self._data['high'], self._data['low']))
        # self._log.info("code=%s now=%6.2f pct=%6.2f pctv2=%6.2f" % ( self._code, self._data['now'], pct, chkVPct))
        self._log.info("  end." )

class Strategy(StrategyTemplate):
    name = 'test2'

    def __init__(self, user, log_handler, main_engine):
        conn = MongoClient('127.0.0.1', 27017)
        db = conn.easyqt
        self.mytbl=db.curdata
        StrategyTemplate.__init__(self, user, log_handler, main_engine)
        self.log.info('init event.')
        self.chks=[]
        config_name = './config/chklist.json'
        with open(config_name, 'r') as f:
            data = json.load(f)
            # print data
            for d in data['chk']:
                self.chks.append((d['c'], d['p']))
                # print d['c']

    def strategy(self, event):
        self.log.info('\n\nStrategy 2 event')
        for idx,row in event.data:
            self.log.info(row)
            #self.mytbl.insert(row.to_dict())

        # chklist = ['002617','600549','300275','000615']
        # print  (type(event.data))
        threads = []
        # [calcStrategy(l) for i in range(5)]
        for td in event.data:
            #print(event.data[td])
            threads.append(calcStrategy(td, event.data[td], self.log, td))
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

