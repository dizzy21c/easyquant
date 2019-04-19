# coding: utf-8
import os
import sys
import redis
import json
import pandas as pd
import numpy as np

class RedisIo(object):
    """Redis操作类"""
    
    def __init__(self, conf):
        self.config = self.file2dict(conf)
        if self.config['passwd'] is None:
            self.r = redis.Redis(host=self.config['redisip'], port=self.config['redisport'], db=self.config['db'])
        else:
            self.r = redis.Redis(host=self.config['redisip'], port=self.config['redisport'], db=self.config['db'], password = self.config['passwd'])
    
    def file2dict(self, path):
        #读取配置文件
        with open(path) as f:
            return json.load(f)
        
    def cleanup(self):
        #清理Redis当前数据库
        self.r.flushdb()

    def lookup_redist_info(self):
        #查询Redis配置
        info = self.r.info()

    def set_key_value(self, key, value):
        #设置键值对key<-->value
        self.r.set(key, value)

    def get_key_value(self, key):
        #查询键值对
        return self.r.get(key)

    def save(self):
        #强行保存数据到硬盘
        return self.r.save()

    def get_keys(self):
        #获取当前数据库里面所有键值
        return self.r.keys()

    def delete_key(self, key):
        #删除某个键
        return self.r.delete(key)

    def push_list_value(self, listname, value):
        #推入到队列
        return self.r.lpush(listname, value)

    def push_list_rvalue(self, list_name, value):
        # print("%s=%s" %(list_name, value))
        return self.r.rpush(list_name, value)

    def pull_list_range(self, listname, starpos=0, endpos=-1):
        #获取队列某个连续片段
        return self.r.lrange(listname, starpos, endpos)

    def get_list_len(self, listname):
        #获取队列长度
        return self.r.llen(listname)

    def push_cur_data(self, code, data, idx=0):
        # print("put cur data")
        self.push_data_value(code, data, dtype='cur', vtype='close', idx=idx)
        self.push_data_value(code, data, dtype='cur', vtype='high', idx=idx)
        self.push_data_value(code, data, dtype='cur', vtype='low', idx=idx)
        self.push_data_value(code, data, dtype='cur', vtype='vol', idx=idx)
        #for backup
        self.push_data_value(code, data, dtype='cur', vtype='volume', idx=idx)
        self.push_data_value(code, data, dtype='cur', vtype='open', idx=idx)
        self.push_data_value(code, data, dtype='cur', vtype='datetime', idx=idx)

        if idx==0:
            #{'name': '"', 'open': 11.19, 'close': 11.1, 'now': 11.47, 'high': 11.63, 'low': 11.19, 'buy': 11.46, 'sell': 11.47, 'turnover': 54845630, 'volume': 629822482.49, 'bid1_volume': 52700, 'bid1': 11.46, 'bid2_volume': 94600, 'bid2': 11.45, 'bid3_volume': 10900, 'bid3': 11.44, 'bid4_volume': 40700, 'bid4': 11.43, 'bid5_volume': 60500, 'bid5': 11.42, 'ask1_volume': 5200, 'ask1': 11.47, 'ask2_volume': 70600, 'ask2': 11.48, 'ask3_volume': 116300, 'ask3': 11.49, 'ask4_volume': 248000, 'ask4': 11.5, 'ask5_volume': 26200, 'ask5': 11.51, 'date': '2019-04-08', 'time': '14:12:33'}
            #{'name': '"', , 'buy': 11.46, 'sell': 11.47,  'bid1_volume': 52700, 'bid1': 11.46, 'bid2_volume': 94600, 'bid2': 11.45, 'bid3_volume': 10900, 'bid3': 11.44, 'bid4_volume': 40700, 'bid4': 11.43, 'bid5_volume': 60500, 'bid5': 11.42, 'ask1_volume': 5200, 'ask1': 11.47, 'ask2_volume': 70600, 'ask2': 11.48, 'ask3_volume': 116300, 'ask3': 11.49, 'ask4_volume': 248000, 'ask4': 11.5, 'ask5_volume': 26200, 'ask5': 11.51, 'date': '2019-04-08', 'time': '14:12:33'}
            self.push_data_value(code, data, dtype='cur', vtype='buy')
            self.push_data_value(code, data, dtype='cur', vtype='sell')
    
    def push_day_data(self, code, data, idx=0):
        self.push_data_value(code, data, vtype='close', idx=idx)
        self.push_data_value(code, data, vtype='high', idx=idx)
        self.push_data_value(code, data, vtype='low', idx=idx)
        self.push_data_value(code, data, vtype='vol', idx=idx)
        #for backup
        self.push_data_value(code, data, vtype='volume', idx=idx)
        self.push_data_value(code, data, vtype='open', idx=idx)
        self.push_data_value(code, data, vtype='date', idx=idx)
    
    def push_data_value(self, code, data, dtype='day', vtype='close', idx=0):
        #listname=self._get_key(code,'day','close')
        if idx==0:
            listname=self._get_key(code, dtype=dtype, vtype=vtype, idx=0)
        else:
            listname=self._get_key(code, dtype=dtype, vtype=vtype, idx=idx)

        if vtype == 'close':
            value=data['now']
        elif vtype == 'vol':
            value = data['volume']
        elif vtype == 'datetime':
            value = "%s %s"%(data['date'], data['time'])
        else:
            value=data[vtype]

        self.push_list_rvalue(listname, value)
    
    def _get_key(self, code, dtype='day', vtype='close', idx=0):
        if idx==0:
            return "%s:%s:%s"%(code, dtype, vtype)
        else:
            return "%s:idx:%s:%s"%(code, dtype, vtype)

    def _get_str_data(self, listname, startpos=0, endpos=-1):
        rl = self.pull_list_range(listname, startpos, endpos) 
        return [v.decode() for v in rl]

    def _get_num_data(self, listname, startpos=0, endpos=-1):
        rl = self.pull_list_range(listname, startpos, endpos) 
        return [json.loads(v.decode()) for v in rl]

    def get_day_df(self, code, startpos=0, endpos=-1):
        c = self.get_day_c(code, startpos, endpos)
        h = self.get_day_h(code, startpos, endpos)
        l = self.get_day_l(code, startpos, endpos)
        o = self.get_day_o(code, startpos, endpos)
        v = self.get_day_v(code, startpos, endpos)
        d = self.get_day_d(code, startpos, endpos)
        #return pd.DataFrame(index=d, data={'close':c, 'vol':v, 'high':h, 'low':l, 'open':o})
        return pd.DataFrame(index=d, data={'close':c, 'vol':v, 'high':h, 'low':l})

   
    def get_day_c(self, code, startpos=0, endpos=-1, idx=0):
        listname=self._get_key(code, vtype='close', idx=idx)
        return self._get_num_data(listname, startpos, endpos)
   
    def get_day_v(self, code, startpos=0, endpos=-1, idx=0):
        listname=self._get_key(code, vtype='vol', idx=idx)
        return self._get_num_data(listname, startpos, endpos)
   
    def get_day_o(self, code, startpos=0, endpos=-1, idx=0):
        listname=self._get_key(code, vtype='open', idx=idx)
        return self._get_num_data(listname, startpos, endpos)
   
    def get_day_h(self, code, startpos=0, endpos=-1, idx=0):
        listname=self._get_key(code, vtype='high', idx=idx)
        return self._get_num_data(listname, startpos, endpos)
   
    def get_day_l(self, code, startpos=0, endpos=-1, idx=0):
        listname=self._get_key(code, vtype='low', idx=idx)
        return self._get_num_data(listname, startpos, endpos)
   
    def get_day_d(self, code, startpos=0, endpos=-1, idx=0):
        listname=self._get_key(code, vtype='date', idx=idx)
        return self._get_str_data(listname, startpos, endpos)
   
    def get_iday_df(self, code, startpos=0, endpos=-1):
        c = self.get_day_c(code, startpos, endpos, 1)
        h = self.get_day_h(code, startpos, endpos, 1)
        l = self.get_day_l(code, startpos, endpos, 1)
        # o = self.get_day_o(code, startpos, endpos, 1)
        v = self.get_day_v(code, startpos, endpos, 1)
        d = self.get_day_d(code, startpos, endpos, 1)
        #return pd.DataFrame(index=d, data={'close':c, 'vol':v, 'high':h, 'low':l, 'open':o})
        return pd.DataFrame(index=d, data={'close':c, 'vol':v, 'high':h, 'low':l})

def main():
    ri = RedisIo('redis.conf')
    ri.lookup_redist_info()
    ri.set_key_value('test1', 1)
    ri.push_list_value('test2', 1)
    ri.push_list_value('test2', 2)

if __name__ == '__main__':
    main()
