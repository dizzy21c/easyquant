# coding: utf-8
import os
import sys
import pymongo
import json
import pandas as pd
import numpy as np

class MongoIo(object):
    """Redis操作类"""
    
    def __init__(self, conf):
        self.config = self.file2dict(conf)
        client = pymongo.MongoClient(self.config['mongoip'], self.config['mongoport'])
        self.db = client[self.config['mongodb']]
        # if self.config['passwd'] is None:
        #     self.r = redis.Redis(host=self.config['redisip'], port=self.config['redisport'], db=self.config['db'])
        # else:
        #     self.r = redis.Redis(host=self.config['redisip'], port=self.config['redisport'], db=self.config['db'], password = self.config['passwd'])
    
    def get_data(self, code, st_start="2017-01-01", st_end="2030-01-01"):
        col =self.db.stock_day
        dtd=col.find({'code':code,'date':{'$gt':st_start}, 'date':{"$lt":st_end}})
        ptd=pd.DataFrame(list(dtd))
        del ptd['_id']
        del ptd['date_stamp']
        ptd.rename(columns={"vol":"volume"}, inplace=True)
        return ptd

    def file2dict(self, path):
        #读取配置文件
        with open(path) as f:
            return json.load(f)
        
    
def main():
    md = MongoIo('mongo.conf')
    md.get_data('000001')
    # d.head

if __name__ == '__main__':
    main()
