import os
import struct
import pandas as pd
import numpy as np
import talib as tdx
import multiprocessing

def readTdxLdayFile(fname="data/sh000001.day"):
  dataSet=[]
  with open(fname,'rb') as fl:
    buffer=fl.read() #读取数据到缓存
    size=len(buffer) 
    rowSize=32 #通信达day数据，每32个字节一组数据
    code=os.path.basename(fname).replace('.day','')
    for i in range(0,size,rowSize): #步长为32遍历buffer
      row=list( struct.unpack('IIIIIfII',buffer[i:i+rowSize]) )
      row[1]=row[1]/100
      row[2]=row[2]/100
      row[3]=row[3]/100
      row[4]=row[4]/100
      row.pop() #移除最后无意义字段
      row.insert(0,code)
      dataSet.append(row) 

  data=pd.DataFrame(data=dataSet,columns=['code','tradeDate','open','high','low','close','amount','vol'])
  data=data.set_index(['tradeDate']).sort_index()
  return code, data

def select1(code, data):
    # 连续三日缩量
    cn = data.close.iloc[-1]
#     df=pd.concat([tdx.MA(data.close, x) for x in (5,10,20,30,60,90,120,250,500,750,1000,1500,2000,2500,) ], axis = 1).dropna()[-1:]
    df=pd.concat([tdx.MA(data.close, x) for x in (5,10,20,30,60,90,120,250,500,750,1000,1500,2000,2500,) ], axis = 1)[-1:]
    df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm500', u'm750', u'm1000', u'm1500', u'm2000', u'm2500']  
    df_c2 = df.m5 > df.m10
    df_c1 = cn > df.m5
    df_c = cn > df.m5
    df_h = df.apply(lambda x:cn > x.max() ,  axis = 1 )
#     df_l = df.apply(lambda x:x.min() >= cl,  axis = 1 )
    
    df['dfh'] = df_h
    df['dfc2'] = df_c2
    df['dfc1'] = df_c1
    df['code'] =code
#     out=df.iloc[-1].apply(lambda x: True if x>cl and x < ch else False)
    df=df.reset_index('tradeDate')
    df=df.set_index(['code','tradeDate'])
    return df

def asyncCalc(fname, queue):
  code, df = readTdxLdayFile(fname)
  queue.put(select1(code, df))
    
def readPath(path):
  files = os.listdir(path)
  # codes=[]
  q = multiprocessing.Queue()
  jobs = []
  # dataSet=[]multiprocessing
  pool_size = multiprocessing.cpu_count()
  pool = multiprocessing.Pool(pool_size)
  output=pd.DataFrame()
  for i in range(0,len(files)):
    fname = os.path.join(path,files[i])
    if os.path.isdir(fname):
      continue
    pool.apply_async(asyncCalc, args=(fname))
    p = multiprocessing.Process(target=asyncCalc, args=(fname, q))
    jobs.append(p)
    p.start()
  
  for p in jobs:
    p.join()

  for j in jobs:
    t = q.get()
    if t is not None:
      output=output.append(t)
  return output

output=readPath('data') #读取目录下面的所有文件
# print(output.head())
output.to_csv('test-org.csv')
output.query('dfh==True and dfc1==True and dfc2==True').to_csv('test-data.csv')