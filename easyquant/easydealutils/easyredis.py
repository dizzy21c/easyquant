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
        return self.r.rpush(list_name, value)

    def pull_list_range(self, listname, starpos=0, endpos=-1):
        #获取队列某个连续片段
        return self.r.lrange(listname, starpos, endpos)

    def get_list_len(self, listname):
        #获取队列长度
        return self.r.llen(listname)

    def push_day_all(self, code, data):
        #listname=self._get_skey(code,'day','close')
        self.push_day_c(code, data['now'])
    
    def push_day_c(self, code, data):
        #listname=self._get_skey(code,'day','close')
        listname=self._get_skey(code)
        value=data
        return self.push_list_rvalue(listname, value)
    
    def _get_skey(self, code, dtype='day', vtype='close'):
        return "%s:%s:%s"%(code, dtype, vtype)

    def _get_ikey(self, code, dtype='day', vtype='close'):
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

   
    def get_day_c(self, code, startpos=0, endpos=-1):
        listname=self._get_skey(code)
        return self._get_num_data(listname, startpos, endpos)
   
    def get_day_v(self, code, startpos=0, endpos=-1):
        listname=self._get_skey(code, vtype='vol')
        return self._get_num_data(listname, startpos, endpos)
   
    def get_day_o(self, code, startpos=0, endpos=-1):
        listname=self._get_skey(code, vtype='open')
        return self._get_num_data(listname, startpos, endpos)
   
    def get_day_h(self, code, startpos=0, endpos=-1):
        listname=self._get_skey(code, vtype='high')
        return self._get_num_data(listname, startpos, endpos)
   
    def get_day_l(self, code, startpos=0, endpos=-1):
        listname=self._get_skey(code, vtype='low')
        return self._get_num_data(listname, startpos, endpos)
   
    def get_day_d(self, code, startpos=0, endpos=-1):
        listname=self._get_skey(code, vtype='date')
        return self._get_str_data(listname, startpos, endpos)
   
    def get_iday_df(self, code, startpos=0, endpos=-1):
        c = self.get_iday_c(code, startpos, endpos)
        h = self.get_iday_h(code, startpos, endpos)
        l = self.get_iday_l(code, startpos, endpos)
        # o = self.get_iday_o(code, startpos, endpos)
        v = self.get_iday_v(code, startpos, endpos)
        d = self.get_iday_d(code, startpos, endpos)
        #return pd.DataFrame(index=d, data={'close':c, 'vol':v, 'high':h, 'low':l, 'open':o})
        return pd.DataFrame(index=d, data={'close':c, 'vol':v, 'high':h, 'low':l})

    def get_iday_c(self, code, startpos=0, endpos=-1):
        listname=self._get_ikey(code)
        return self._get_num_data(listname, startpos, endpos)

    def get_iday_v(self, code, startpos=0, endpos=-1):
        listname=self._get_ikey(code, vtype='vol')
        return self._get_num_data(listname, startpos, endpos)
   
    def get_iday_o(self, code, startpos=0, endpos=-1):
        listname=self._get_ikey(code, vtype='open')
        return self._get_num_data(listname, startpos, endpos)
   
    def get_iday_h(self, code, startpos=0, endpos=-1):
        listname=self._get_ikey(code, vtype='high')
        return self._get_num_data(listname, startpos, endpos)
   
    def get_iday_l(self, code, startpos=0, endpos=-1):
        listname=self._get_ikey(code, vtype='low')
        return self._get_num_data(listname, startpos, endpos)
   
    def get_iday_d(self, code, startpos=0, endpos=-1):
        listname=self._get_ikey(code, vtype='date')
        return self._get_str_data(listname, startpos, endpos)
   
   
def main():
    ri = RedisIo('redis.conf')
    ri.lookup_redist_info()
    ri.set_key_value('test1', 1)
    ri.push_list_value('test2', 1)
    ri.push_list_value('test2', 2)

if __name__ == '__main__':
    main()
