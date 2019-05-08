# import pymongo
import redis
from threading import Thread
from easyquant.qafetch.QATdx import QATdx as tdx

# mhost='localhost'
# mport=27017
rhost='localhost'
rport=6379

# client= pymongo.MongoClient(mhost, mport)
# db = client.quantaxis
#idxd = db.index_day

rs = redis.Redis(host=rhost, port=rport, db=0)

def rpush(code, flg, dtype, data):
  rs.rpush("%s:%s:%s"%(code, flg, dtype), data[dtype])

def allpush(code,flg, tbl_data, dtype=0):
  for x in tbl_data:
    rpush(code,flg,'close',x)
    rpush(code,flg,'open',x)
    rpush(code,flg,'high',x)
    rpush(code,flg,'low',x)
    rpush(code,flg,'vol',x)
    if dtype==0:
      rpush(code,flg,'date',x)
    else:
      rpush(code,flg,'datetime',x)

def convert_min(code, flg, st_date, col, mtype):
  dtd=col.find({'code':code,'date':{'$gt':st_date}, 'type':mtype})
  allpush(code, flg, dtd, 1)

def convert(code, flg, st_date, col):
  dtd=col.find({'code':code,'date':{'$gt':st_date}})
  allpush(code, flg, dtd)

def date_conv(st_date):
  st_info = db.stock_list
  st_list = list(st_info.find())
  col_s =db.stock_day
  for x in st_list:
    #t = Thread(target=convert,args=(x['code'],'day', st_date, col_s))
    #t.start()
    convert(x['code'],'day', st_date, col_s)
    #break

  #col_s_m = db.stock_min
  idx_info=db.index_list
  idx_list=list(idx_info.find())
  col_i=db.index_day
  for x in idx_list:
    #t = Thread(target=convert,args=(x['code'],'idx:day', st_date, col_i))
    #t.start()
    convert(x['code'], 'idx:day', st_date, col_i)
    #break

  col_idx_min=db.index_min
  for x in idx_list:
    #t = Thread(target=onvert_min,args=(x['code'], 'idx:5min',st_date,col_idx_min,'5min'))
    #t.start()
    convert_min(x['code'], 'idx:5min',st_date,col_idx_min,'5min') 
    #break

#convert('600718','2018-01-01')
st_date='2013-01-01'
date_conv(st_date)

def main():
  pass
    # ri = RedisIo('redis.conf')
    # ri.lookup_redis_info()
    # ri.set_key_value('test1', 1)
    # ri.push_list_value('test2', 1)
    # ri.push_list_value('test2', 2)

if __name__ == '__main__':
  main()
