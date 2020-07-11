# coding: utf-8
import os
import sys
import pymongo as mongo
import json
import pandas as pd
import numpy as np
from datetime import date
import time
from QUANTAXIS.QAFetch import QATdx as tdx
from easyquant.easydealutils.easytime import EasyTime

class MongoIo(object):
    """Redis操作类"""
    
    def __init__(self, host='127.0.0.1', port=27017, database='quantaxis'):
        # self.config = self.file2dict(conf)
        client = mongo.MongoClient(host, port)
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
            # st_end = "2030-12-31"
            st_end = "2030-12-31 23:59:59"
        if type == 'D':
            if isinstance(code, list):
                dtd=self.db[table].find({'code':{'$in' : code},'date':{'$gte':st_start, "$lte":st_end}})
            else:
                dtd=self.db[table].find({'code':code,'date':{'$gte':st_start, "$lte":st_end}})
        else:
            if isinstance(code, list):
                dtd=self.db[table].find({'code':{'$in':code},'date':{'$gte':st_start, "$lte":st_end}, 'type':type})
            else:
                dtd=self.db[table].find({'code':code,'date':{'$gte':st_start, "$lte":st_end}, 'type':type})
        ptd=pd.DataFrame(list(dtd))
        if len(ptd) > 0:
            del ptd['_id']
            del ptd['date_stamp']
            if type == 'D':
                ptd.date = pd.to_datetime(ptd.date)
                ptd = ptd.set_index(["date","code"])
            else:
                ptd.date = pd.to_datetime(ptd.date)
                ptd.datetime= pd.to_datetime(ptd.datetime)
                ptd = ptd.set_index(["datetime","code"])
        # ptd.rename(columns={"vol":"volume"}, inplace=True)
        return ptd
    
    def get_stock_day(self, code, st_start=None, st_end=None):
        if st_start is None:
            st_start = self.st_start
        return self._get_data(code, 'stock_day', st_start, st_end)
  
    def get_stock_min(self, code, st_start=None, st_end=None, freq=5):
        if st_start is None:
            st_start = self.st_start_15min
            
        return self._get_data(code, 'stock_min', st_start, st_end, "%dmin"%freq)

    def get_stock_min_realtime(self, code, st_start=None, st_end=None, freq=5):
        if st_start is None:
            st_start = self.st_start_5min
        if st_end is None:
            st_end = "2030-12-31 23:59:59"

        data_min = self.get_stock_min(code=code, freq=freq)
        if len(data_min) > 0:
            if freq < (time.time() - data_min.index[-1][0].timestamp()) / 60:
                start = data_min.index[-1][0].strftime('%Y-%m-%d %H:%M:01')  ## %S=>01
                add_df = tdx.QA_fetch_get_stock_min(code, start=start, end=st_end, frequence='%dmin' % freq)
                if len(add_df) > 0:
                    add_df.drop(['date_stamp', 'datetime'], axis=1, inplace=True)
                    data_min = data_min.append(add_df, sort=True)
                    ## save to db
        else:
            data_min = tdx.QA_fetch_get_stock_min(code, start=st_start, end=st_end, frequence='%dmin' % freq)
            if len(data_min) > 0:
                data_min.drop(['date_stamp', 'datetime'], axis=1, inplace=True)

        return data_min

    def get_index_day(self, code, st_start=None, st_end=None):
        if st_start is None:
            st_start = self.st_start
            
        return self._get_data(code, 'index_day', st_start, st_end)

    def get_index_min(self, code, st_start=None, st_end=None, freq=5):
        if st_start is None:
            st_start = self.st_start_15min
            
        return self._get_data(code, 'index_min', st_start, st_end, "%dmin"%freq)

    def get_index_min_realtime(self, code, st_start=None, st_end=None, freq=5):
        if st_start is None:
            st_start = self.st_start_5min
        if st_end is None:
            st_end = "2030-12-31 23:59:59"
        
        data_min = self.get_index_min(code=code, freq=freq)
        if len(data_min) > 0:
            if freq < (time.time() - data_min.index[-1][0].timestamp()) / 60:
                start=data_min.index[-1][0].strftime('%Y-%m-%d %H:%M:01') ## %S=>01
                add_df=tdx.QA_fetch_get_index_min(code,start=start,end=st_end, frequence='%dmin' % freq)
                if len(add_df) > 0:
                    add_df.drop(['date_stamp','datetime'],axis=1,inplace=True)
                    data_min=data_min.append(add_df, sort=True)
        else:
            data_min=tdx.QA_fetch_get_index_min(code,start=st_start,end=st_end, frequence='%dmin' % freq)
            if len(data_min) > 0:
                data_min.drop(['date_stamp','datetime'],axis=1,inplace=True)
        
        return data_min

    def file2dict(self, path):
        #读取配置文件
        with open(path) as f:
            return json.load(f)

    def save(self, table, data):
        self.db[table].insert_many(
            [data]
        )

    def save_data_min(self, data, idx=0):
        if idx == 0:
            pass
        else:
            pass

    def save_realtime(self, data):
        table = 'realtime_{}'.format(date.today())
        # self.db[table].insert_many(
        #     [data]
        # )
        self.db[table].replace_one({'_id':data['_id']}, data, True)

    def upd_data_min(self, df_data_min, json_data, minute):
        # index_time =pd.to_datetime(easytime.get_minute_date(minute=5))
        et = EasyTime()
        index_time = pd.to_datetime(et.get_minute_date_str(minute=minute, str_date=json_data['datetime']))
        begin_time = pd.to_datetime(et.get_begin_trade_date(minute=minute, str_date=json_data['datetime']))
        if len(df_data_min) > 0:
            sum_df=df_data_min.loc[df_data_min.index > begin_time]
            old_vol = sum_df['vol'].sum()
            old_amount = sum_df['amount'].sum()
            now_price = json_data['now']
            if index_time in df_data_min.index:
                if now_price > df_data_min.loc[index_time, 'high']:
                    df_data_min.loc[index_time, 'high'] = now_price
                if now_price < df_data_min.loc[index_time, 'low']:
                    df_data_min.loc[index_time, 'low'] = now_price
                df_data_min.loc[index_time, 'close'] = now_price
                df_data_min.loc[index_time, 'vol'] = json_data['volume'] - old_vol
                df_data_min.loc[index_time, 'amount'] = json_data['amount'] - old_amount
            else:
                # if self.code == '600822':
                #     print("2 code=%s, data=%d" % (self.code, len(df_data_min)))
                df_data_min.loc[index_time] = [0 for x in range(len(df_data_min.columns))]
                df_data_min.loc[index_time, 'code'] = json_data['code']
                df_data_min.loc[index_time, 'open'] = now_price
                df_data_min.loc[index_time, 'high'] = now_price
                df_data_min.loc[index_time, 'low'] = now_price
                df_data_min.loc[index_time, 'close'] = now_price
                df_data_min.loc[index_time, 'vol'] = json_data['volume'] - old_vol
                df_data_min.loc[index_time, 'amount'] = json_data['amount'] - old_amount
        else: ##first day ???
            pass

        return df_data_min

def main():
    md = MongoIo()
    md.get_stock_day('000001')
    # d.head

if __name__ == '__main__':
    main()
