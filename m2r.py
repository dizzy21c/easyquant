import pymongo
import redis
# from threading import Thread
import multiprocessing

mhost='localhost'
mport=27017
rhost='localhost'
rport=6379

client= pymongo.MongoClient(mhost, mport, maxPoolSize=100)

def getDb():
  return client.quantaxis

rs = redis.Redis(host=rhost, port=rport, db=0)

def rpush(code, flg, dtype, data):
  rs.rpush("%s:%s:%s"%(code, flg, dtype), data[dtype])

def allpush(code,flg, tbl_data, dtype=0):
  # print(code)
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

def convert_min(code, flg, st_date, mtype):
  col = getDb().index_min
  dtd=col.find({'code':code,'date':{'$gt':st_date}, 'type':mtype})
  allpush(code, flg, dtd, 1)

def convert(code, flg, st_date):
  if flg == "day":
    col = getDb().stock_day
  elif flg == "idx:day":
    col = getDb().index_day

  dtd=col.find({'code':code,'date':{'$gt':st_date}})
  allpush(code, flg, dtd)
  # return "ok"

# def test_func(code,code2,s,d):
  # print(code)

def date_conv(st_date):
  pool = multiprocessing.Pool(processes = 8)
  st_info = getDb().stock_list
  st_list = list(st_info.find())
  # col_s =db.stock_day
  for x in st_list:
    #t = Thread(target=convert,args=(x['code'],'day', st_date, col_s))
    #t.start()
    # convert(x['code'],'day', st_date, col_s)
    # print(x)
    # pool.apply_async(convert, (x['code'],"day", st_date, col_s,))
    # pool.apply(func=convert, args=(x['code'],'day', st_date, col_s,))
    pool.apply_async(func=convert, args=(x['code'],"day",st_date,))
    # break

  # pool2 = multiprocessing.Pool(processes = 8)
  #col_s_m = db.stock_min
  idx_info=getDb().index_list
  idx_list=list(idx_info.find())
  # col_i=db.index_day
  for x in idx_list:
    #t = Thread(target=convert,args=(x['code'],'idx:day', st_date, col_i))
    #t.start()
    # convert(x['code'], 'idx:day', st_date, col_i)
    pool.apply_async(convert, (x['code'],'idx:day', st_date,))
    # break

  # pool = multiprocessing.Pool(processes = 8)
  # col_idx_min=db.index_min
  for x in idx_list:
    #t = Thread(target=onvert_min,args=(x['code'], 'idx:5min',st_date,col_idx_min,'5min'))
    #t.start()
    # convert_min(x['code'], 'idx:5min',st_date,col_idx_min,'5min') 
    pool.apply_async(func=convert_min,args=(x['code'], 'idx:5min',st_date,'5min',))
    # break

  pool.close()
  pool.join()

#convert('600718','2018-01-01')

if __name__ == "__main__":
  # pool = multiprocessing.Pool(processes = 8)
  st_date='2016-01-01'
  date_conv(st_date)

