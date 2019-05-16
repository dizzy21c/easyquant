# import pymongo
import redis
from threading import Thread
from easyquant import RedisIo
from codelist_utils import get_udf_code_list
from easyquant import QATdx as tdx

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

def data_conv(st_date, codes, idx=0, redis=redis, end_date = "2020-12-31"):
  for x in codes:
    if x[0:2] == "sh":
      x = x[3:]
    print("read data=%s" % x)
    tmp_df = redis.get_day_df(x, idx)
    l = len(tmp_df)
    if l > 0:
      st_date = tmp_df['date'][l-1]
    if idx == 0:
      new_df = tdx.QA_fetch_get_stock_day(x, st_date,end_date)
    else:
      new_df = tdx.QA_fetch_get_stock_day(x, st_date,end_date)
      
    for idx,row in new_df.iterrows():
      data_dict={'code':row.code, 'open':row.open, 'close':row.close, 'high':row.high, 'low':row.low, 'date':row.date, 'volume':row.vol, 'vol':row.vol, 'now':row.close}
      redis.push_day_data(row.code,data_dict)

    #t = Thread(target=convert,args=(x['code'],'day', st_date, col_s))
    #t.start()
    #convert(x['code'],'day', st_date, col_s)
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
# st_date='2013-01-01'
# data_conv(st_date)
def main():
  st_date="2013-01-01"
  stock_list, index_list, _ = get_udf_code_list()
  redis = RedisIo('redis.conf')
  data_conv(st_date, stock_list, redis=redis, idx=0)
  

  # data_conv(st_date)
  # pass
    # ri = RedisIo('redis.conf')
    # ri.lookup_redis_info()
    # ri.set_key_value('test1', 1)
    # ri.push_list_value('test2', 1)
    # ri.push_list_value('test2', 2)

if __name__ == '__main__':
  main()
