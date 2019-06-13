# coding: utf-8
import os
import sys
import redis
import json
import time
import pandas as pd
import numpy as np

class RedisIo(object):
    """Redis操作类"""
    
    def __init__(self, conf='redis.conf'):
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

    def lookup_redis_info(self):
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

    def pop_list_value(self, listname):
        #推入到队列
        return self.r.lpop(listname)

    def pop_list_rvalue(self, list_name):
        # print("%s=%s" %(list_name, value))
        return self.r.rpop(list_name)

    def rpop(self, list_name):
        # test only
        # print("%s=%s" %(list_name, value))
        value = self.r.rpop(list_name)
        if value is None:
            return ""
        else:
            return value.decode()

    # def rpop_day_df(self, code, dtype="day", idx=0):
    def rpop_day_df(self, code, idx=0):
        dtype="day"
        self.rpop(self._get_key(code, dtype=dtype, idx=idx))
        # self.rpop(self._get_key(code,idx=idx))
        # self.rpop(self._get_key(code,idx=idx))
        # self.rpop(self._get_key(code,idx=idx))
        # self.rpop(self._get_key(code,idx=idx))
        # self.rpop(self._get_key(code,idx=idx))
        # self.rpop(self._get_key(code,idx=idx))

    def get_last_date(self, code, dtype="day", idx=0):
        list = self.get_data_value(code, dtype=dtype, startpos=-1, endpos=-1, idx=idx)
        if list == []:
            return None
        else:
            return self.list2ochlvad(list[0])[6]

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

    def set_cur_data(self, code, data, idx=0):
        dtype = "now"
        listname=self._get_key(code,dtype,idx)
        self.set_key_value(listname, data)

    def get_cur_data(self, code, idx=0):
        dtype = "now"
        listname=self._get_key(code,dtype,idx)
        return self.get_key_value(listname)

    def push_cur_data(self, code, data, idx=0, last_vol = 0):
        dtype = "cur"
        listname=self._get_key(code,dtype,idx)
        value = self.dict2ochlvadt(data, last_vol)
        self.push_list_rvalue(listname, value)
    
    def push_day_data(self, code, data, idx=0):
        last_date = self.get_last_date(code, idx=idx)
        # self.set_read_flg(code, value=0)
        if last_date == data['date']:
            self.rpop_day_df(code, idx=idx)

        self.push_data_value(code, data, idx=idx)
        # self.set_log_date(code, data, idx = idx)

    # def push_day_data(self, code, data, idx=0):
    #     # listname=self._get_key(code,vtype='date',idx=idx)
    #     # last_date = self.rpop(listname)
    #     last_date = self.get_last_date(code, idx=idx)
    #     self.set_read_flg(code, value=0)
    #     if last_date == data['date']:
    #         self.rpop_day_df(code, idx=idx)
    #         # self.rpop(self._get_key(code,idx=idx))
    #         # self.rpop(self._get_key(code,idx=idx))
    #         # self.rpop(self._get_key(code,idx=idx))
    #         # self.rpop(self._get_key(code,idx=idx))
    #         # self.rpop(self._get_key(code,idx=idx))
    #         # self.rpop(self._get_key(code,idx=idx))
    #         # self.rpop(self._get_key(code,idx=idx))
    #     # else:
    #     #     self.push_list_rvalue(listname,last_date)
    #     self.push_data_value(code, data, idx=idx)

    #     self.push_data_value(code, data, idx=idx)
    #     self.push_data_value(code, data, idx=idx)
    #     # self.push_data_value(code, data, idx=idx)
    #     self.push_data_value(code, data, idx=idx)
    #     self.push_data_value(code, data, idx=idx)
    #     self.push_data_value(code, data, idx=idx)
    #     self.set_read_flg(code)
    #     self.set_log_date(code, data, idx = idx)

    # def set_log_date(self, code, data, dtype='day', idx=0):
    #     vtype = "logtime"
    #     listname=self._get_key(code,dtype,vtype,idx)

    #     # if 'time' in data.keys():
    #     value = "%s %s"%(data['date'], data['time'])
    #     self.set_key_value(listname, value)
    
    # def set_read_flg(self, code, value=1, dtype='day', idx=0):
    #     vtype = "rwflg"
    #     listname=self._get_key(code,dtype,vtype,idx)
    #     self.set_key_value(listname, value)
    
    # def is_read_flg(self, code, dtype='day', idx=0):
    #     vtype = "rwflg"
    #     listname=self._get_key(code,dtype,vtype,idx)
    #     value = self.get_key_value(listname)
    #     return value is None or "1" == value
    
    def dict2ochlvadt(self, data, last_vol = 0, last_amount = 0):
        ##      O  C  H  L  V  A D T
        rtn = "%s|%s|%s|%s|%s|%s" % (data['open'],data['now'],data['high'],data['low'],data['turnover'] / 100 - last_vol, data['amount'] - last_amount)
        rtn = "%s|%s|%s %s|%s" % (rtn, data['date'], data['date'],data['time'], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        return rtn

    def dict2ochlvad(self, data, last_vol = 0, last_amount = 0):
        ##      O  C  H  L  V  A #D#
        rtn = "%s|%s|%s|%s|%s|%s" % (data['open'],data['now'],data['high'],data['low'],data['turnover'] / 100 - last_vol, data['volume'] - last_amount)
        if 'time' in data.keys():
            rtn = "%s|%s|%s %s" % (rtn, data['date'], data['date'],data['time'])
        else:
            rtn = "%s|%s" % (rtn, data['date'])
        return rtn

    def list2ochlvad(self, data):
        rtn = []
        for ns in data.split('|'):
            if "-" in ns: # 2019-12-31 [12:59:59]
                rtn.append(ns)
            else:
                rtn.append(float(ns))
        return rtn

    def push_data_value(self, code, data, dtype='day', idx=0, last_vol = 0, last_amount = 0):
        listname=self._get_key(code,dtype,idx)
        value = self.dict2ochlvad(data, last_vol, last_amount)
        self.push_list_rvalue(listname, value)

        #if idx==0:
    # def push_data_value(self, code, data, dtype='day', idx=0, last_vol = 0):
    #     listname=self._get_key(code,dtype,vtype,idx)
    #     #if idx==0:
    #     #    listname=self._get_key(code, dtype=dtype, idx=0)
    #     #else:
    #     #    listname=self._get_key(code, dtype=dtype, idx=idx)

    #     if vtype == 'close':
    #         value=data['now']
    #     elif vtype == 'vol':
    #         value = data['turnover'] / 100 - last_vol
    #     elif vtype == 'volume':
    #         value = data['turnover'] / 100 - last_vol
    #     elif vtype == 'datetime':
    #         value = "%s %s"%(data['date'], data['time'])
    #     else:
    #         value=data[vtype]

    #     self.push_list_rvalue(listname, value)
    
    def _get_key(self, code, dtype='day', idx=0):
        if idx==0:
            return "%s:%s"%(code, dtype)
        else:
            return "%s:idx:%s"%(code, dtype)

    # def _get_key(self, code, dtype='day', idx=0):
    #     if idx==0:
    #         return "%s:%s:%s"%(code, dtype, vtype)
    #     else:
    #         return "%s:idx:%s:%s"%(code, dtype, vtype)

    def _get_str_data(self, listname, startpos=0, endpos=-1):
        rl = self.pull_list_range(listname, startpos, endpos) 
        return [v.decode() for v in rl]

    def _get_num_data(self, listname, startpos=0, endpos=-1):
        rl = self.pull_list_range(listname, startpos, endpos) 
        return [json.loads(v.decode()) for v in rl]

    def _sdata2dictdata(self, sina_data):
        str = sina_data.decode('utf8').replace('"','').replace('\'','"')
        return json.loads(str)
        
    def get_day_ps(self, data_df, sina_data):
        sdata = self._sdata2dictdata(sina_data)
        def_ps = pd.Series()
        if sdata['open'] <= 0:
           return def_ps

        len_d = len(data_df)
        if len_d <= 0:
           return def_ps
        C = data_df.close.append(pd.Series([sdata['now']], indexs=[len_d]))
        return C
        

    def get_day_ps_chl(self, data_df, sina_data):
        sdata = self._sdata2dictdata(sina_data)
        def_ps = pd.Series()
        if sdata['open'] <= 0:
           return def_ps, def_ps, def_ps

        len_d = len(data_df)
        if len_d <= 0:
           return def_ps, def_ps, def_ps

        C = data_df.close.append(pd.Series([sdata['now']], indexs=[len_d]))
        H = data_df.high.append(pd.Series([sdata['high']], indexs=[len_d]))
        L = data_df.low.append(pd.Series([sdata['low']], indexs=[len_d]))
        return C,H,L

    def get_day_ps_ochlva(self, data_df, sina_data):
        C,H,L = self.get_day_ps_chl(data_df, sina_data)
        len_d = len(C)
        if len_d <= 0:
           return C,C,C,C,C,C

        sdata = self._sdata2dictdata(sina_data)
        O = data_df.open.append(pd.Series([sdata['open']], indexs=[len_d]))
        V = data_df.vol.append(pd.Series([sdata['turnover']], indexs=[len_d]))
        A = data_df.amount.append(pd.Series([sdata['volume']], indexs=[len_d]))
        return O,C,H,L,V,A

    def get_day_df(self, code, startpos=0, endpos=-1,idx=0):
        return self.get_data_df(code, dtype="day", startpos=startpos, endpos=endpos, idx=idx)
        # c = self.get_day_c(code, startpos, endpos,idx)
        # h = self.get_day_h(code, startpos, endpos,idx)
        # l = self.get_day_l(code, startpos, endpos,idx)
        # o = self.get_day_o(code, startpos, endpos,idx)
        # v = self.get_day_v(code, startpos, endpos,idx)
        # d = self.get_day_d(code, startpos, endpos,idx)
        # cn = len(c)
        # if cn == len(h) and cn == len(l) and cn == len(o) and cn == len(v) and cn == len(d):
        # #return pd.DataFrame(index=d, data={'close':c, 'vol':v, 'high':h, 'low':l, 'open':o})
        #   return pd.DataFrame(data={'close':c, 'open':o, 'volume':v, 'high':h, 'low':l,'date':d})
        # else:
        #   print(" code=%s data error. " %code)
        #   return None

    def get_data_df(self, code, dtype="day", startpos=0, endpos=-1, idx=0):
        data = self.get_data_value(code, dtype=dtype, startpos=startpos, endpos=endpos, idx=idx)
        o = []
        c = []
        h = []
        l = []
        v = []
        a = []
        d = []
        for nd in data:
            snd = self.list2ochlvad(nd)
            o.append(snd[0])
            c.append(snd[1])
            h.append(snd[2])
            l.append(snd[3])
            v.append(snd[4])
            a.append(snd[5])
            d.append(snd[6])
        # return pd.DataFrame(data={'close':c, 'open':o, 'vol':v, 'high':h, 'low':l,'amount':a, 'date':d})
        return pd.DataFrame(data={'close':c, 'open':o, 'vol':v, 'high':h, 'low':l,'amount':a, 'date':d})

    def get_data_value(self, code, dtype='day', startpos=0, endpos=-1, idx=0):
        listname=self._get_key(code,dtype,idx)
        return self._get_str_data(listname, startpos, endpos)
   
    # def get_data_value(self, code, dtype='day', startpos=0, endpos=-1, idx=0):
    #     listname=self._get_key(code,dtype,vtype,idx)
    #     if vtype == "date" or vtype == "datetime":
    #         return self._get_str_data(listname, startpos, endpos)
    #     else:
    #         return self._get_num_data(listname, startpos, endpos)
   
    # def get_day_c(self, code, startpos=0, endpos=-1, idx=0):
    #     return self.get_data_value(code, startpos=startpos, endpos=endpos, idx=idx)
   
    # def get_day_v(self, code, startpos=0, endpos=-1, idx=0):
    #     return self.get_data_value(code, startpos=startpos, endpos=endpos, idx=idx)
   
    # def get_day_o(self, code, startpos=0, endpos=-1, idx=0):
    #     return self.get_data_value(code, startpos=startpos, endpos=endpos, idx=idx)
   
    # def get_day_h(self, code, startpos=0, endpos=-1, idx=0):
    #     return self.get_data_value(code, startpos=startpos, endpos=endpos, idx=idx)
   
    # def get_day_l(self, code, startpos=0, endpos=-1, idx=0):
    #     return self.get_data_value(code, startpos=startpos, endpos=endpos, idx=idx)
   
    # def get_day_d(self, code, startpos=0, endpos=-1, idx=0):
    #     return self.get_data_value(code, startpos=startpos, endpos=endpos, idx=idx)
   
def main():
    ri = RedisIo('redis.conf')
    ri.lookup_redis_info()
    ri.set_key_value('test1', 1)
    ri.push_list_value('test2', 1)
    ri.push_list_value('test2', 2)

if __name__ == '__main__':
    main()
