# coding: utf-8
import os
import sys
import pymongo
import json
import pandas as pd
import numpy as np
from datetime import date

class MongoIo(object):
    """Redis操作类"""
    
    def __init__(self, host='127.0.0.1', port=27017, database='quantaxis'):
        # self.config = self.file2dict(conf)
        client = pymongo.MongoClient(host, port)
        self.db = client[database]
        self.st_start = '2018-01-01'
        # self.st_end = '2030-12-31'
        self.st_start_1min = '2020-01-01'
        self.st_start_5min = '2020-01-01'
        self.st_start_15min = '2020-01-01'
        self.st_start_30min = '2020-01-01'
        self.st_start_60min = '2020-01-01'
        # self.st_end_day = '2030-12-31'
        # if self.config['passwd'] is None:
        #     self.r = redis.Redis(host=self.config['redisip'], port=self.config['redisport'], db=self.config['db'])
        # else:
        #     self.r = redis.Redis(host=self.config['redisip'], port=self.config['redisport'], db=self.config['db'], password = self.config['passwd'])
    
    def _get_data(self, code, table, st_start, st_end, type='D'):
        if st_end is None:
            st_end = "2030-12-31"
        if type == 'D':
            if isinstance(code, list):
                dtd=self.db[table].find({'code':{'$in' : code},'date':{'$gt':st_start, "$lt":st_end}})
            else:
                dtd=self.db[table].find({'code':code,'date':{'$gt':st_start, "$lt":st_end}})
        else:
            if isinstance(code, list):
                dtd=self.db[table].find({'code':{'$in':code},'date':{'$gt':st_start, "$lt":st_end}, 'type':type})
            else:
                dtd=self.db[table].find({'code':code,'date':{'$gt':st_start, "$lt":st_end}, 'type':type})
        ptd=pd.DataFrame(list(dtd))
        if len(ptd) > 0:
            del ptd['_id']
            del ptd['date_stamp']
            if type == 'D':
                ptd.date = pd.to_datetime(ptd.date)
                ptd = ptd.set_index(["date"])
            else:
                ptd.date = pd.to_datetime(ptd.date)
                ptd.datetime= pd.to_datetime(ptd.datetime)
                ptd = ptd.set_index(["datetime"])
        # ptd.rename(columns={"vol":"volume"}, inplace=True)
        return ptd
    
    def get_stock_day(self, code, st_start=None, st_end=None):
        if st_start is None:
            st_start = self.st_start
        return self._get_data(code, 'stock_day', st_start, st_end)
  
    def get_stock_min(self, code, st_start=None, st_end=None, type="15min"):
        if st_start is None:
            st_start = self.st_start_15min
            
        return self._get_data(code, 'stock_min', st_start, st_end, type)
  
    def get_index_day(self, code, st_start=None, st_end=None):
        if st_start is None:
            st_start = self.st_start
            
        return self._get_data(code, 'index_day', st_start, st_end)

    def get_index_min(self, code, st_start=None, st_end=None, type="15min"):
        if st_start is None:
            st_start = self.st_start_15min
            
        return self._get_data(code, 'index_min', st_start, st_end, type)

    def file2dict(self, path):
        #读取配置文件
        with open(path) as f:
            return json.load(f)

    def save(self, table, data):
        self.db[table].insert_many(
            [data]
        )

    def save_realtime(self, data):
        table = 'realtime_{}'.format(date.today())
        self.db[table].insert_many(
            [data]
        )


def main():
    md = MongoIo()
    md.get_stock_day('000001')
    # d.head

if __name__ == '__main__':
    main()
