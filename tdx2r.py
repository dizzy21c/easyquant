# import pymongo
import redis
from threading import Thread
from easyquant import RedisIo
from codelist_utils import get_udf_code_list
from easyquant import QATdx as tdx
import json

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

def readTdx(code, st_date, end_date, idx=0, re = 3):
  if idx == 0:
    new_df = tdx.QA_fetch_get_stock_day(code, st_date,end_date)
  else:
    new_df = tdx.QA_fetch_get_index_day(code, st_date,end_date)

  if new_df is None and re > 0:
    return readTdx(code, st_date, end_date, idx, re - 1)

  return new_df
    
def data_conv(st_date, codes, idx=0, redis=redis, end_date = "2020-12-31", last_date="2020-05-17"):
  nc=len(codes)
  i = 0
  for x in codes:
    i = i + 1
    if x[0:2] == "sh":
      x = x[2:]
    print("read data : %d/%d => %5.2f" % (i, nc,  i / nc * 100 ))
    tmp_date = redis.get_last_date(x)
    if tmp_date is not None:
      st_date = tmp_date

    if tmp_date == last_date:
      continue
    # if idx == 0:
    #   new_df = tdx.QA_fetch_get_stock_day(x, st_date,end_date)
    # else:
    #   new_df = tdx.QA_fetch_get_stock_day(x, st_date,end_date)
    new_df = readTdx(x, st_date, end_date, idx) 
    # if new_df is not None and len(new_df) > 0:
    if new_df is None:
      print("tdx code %s is None." % x)
      continue

    for _,row in new_df.iterrows():
      # print(i) 
      data_dict={'code':row.code, 'open':row.open, 'close':row.close, 'high':row.high, 'low':row.low, 'date':row.date, 'volume':row.vol, 'vol':row.vol, 'now':row.close}
      redis.push_day_data(row.code,data_dict)

    #t = Thread(target=convert,args=(x['code'],'day', st_date, col_s))
    #t.start()
    #convert(x['code'],'day', st_date, col_s)
    #break

  # #col_s_m = db.stock_min
  # idx_info=db.index_list
  # idx_list=list(idx_info.find())
  # col_i=db.index_day
  # for x in idx_list:
  #   #t = Thread(target=convert,args=(x['code'],'idx:day', st_date, col_i))
  #   #t.start()
  #   convert(x['code'], 'idx:day', st_date, col_i)
  #   #break

  # col_idx_min=db.index_min
  # for x in idx_list:
  #   #t = Thread(target=onvert_min,args=(x['code'], 'idx:5min',st_date,col_idx_min,'5min'))
  #   #t.start()
  #   convert_min(x['code'], 'idx:5min',st_date,col_idx_min,'5min') 
  #   #break

#convert('600718','2018-01-01')
# st_date='2013-01-01'
# data_conv(st_date)

def get_code_list(idx=0):
  stock_list=[]
  if idx == 0:
    config = "config/sh_list.json"
    with open(config, "r") as f:
      data = json.load(f)
      stock_list = stock_list + data['code']

    config = "config/sz_list.json"
    with open(config, "r") as f:
      data = json.load(f)
      stock_list = stock_list + data['code']

    config = "config/cyb_list.json"
    with open(config, "r") as f:
      data = json.load(f)
      stock_list = stock_list + data['code']

    config = "config/zxb_list.json"
    with open(config, "r") as f:
      data = json.load(f)
      stock_list = stock_list + data['code']
  else:
    config = "config/index_list.json"
    with open(config, "r") as f:
      data = json.load(f)
      stock_list = stock_list + data['code']

    config = "config/bk_list.json"
    with open(config, "r") as f:
      data = json.load(f)
      stock_list = stock_list + data['code']
    
  return stock_list

def main():
  redis = RedisIo('redis.conf')
  st_date="2013-01-01"
  idx=0
  stock_list = get_code_list(idx)
  data_conv(st_date, stock_list, idx=idx, redis=redis)
  idx=1
  stock_list = get_code_list(idx)
  data_conv(st_date, stock_list, idx=idx, redis=redis)
  # data_conv(st_date)
  # pass
    # ri = RedisIo('redis.conf')
    # ri.lookup_redis_info()
    # ri.set_key_value('test1', 1)
    # ri.push_list_value('test2', 1)
    # ri.push_list_value('test2', 2)

if __name__ == '__main__':
  main()
