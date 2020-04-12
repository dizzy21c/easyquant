import os
import struct
import pandas as pd
import numpy as np
import talib as tdx

def readTdxLdayPath(path):
  files = os.listdir(path)
  codes=[]
  dataSet=[]
  for i in range(0,len(files)):
    fname = os.path.join(path,files[i])
    if os.path.isdir(fname):
      continue
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
      codes.append(code)
  data=pd.DataFrame(data=dataSet,columns=['code','tradeDate','open','high','low','close','amount','vol'])
  data=data.set_index(['code','tradeDate'])
  return codes, data

def select1(code,data):
    # 连续三日缩量
    cn = data.close.iloc[-1]
#     ch= data.close.iloc[-1] * 1.1
#     cl= data.close.iloc[-1] * 0.9
#     ch= data.close * 1.1
#     cl = data.close * 0.9
    
#     df=pd.concat([tdx.MA(data.close, x) for x in (5,10,20,30,60,90,120,250,500,750,1000,1500,2000,2500,) ], axis = 1).dropna()[-1:]
    df=pd.concat([tdx.MA(data.close, x) for x in (5,10,20,30,60,90,120,250,500,750,1000,1500,2000,2500,) ], axis = 1)[-1:]
    df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm500', u'm750', u'm1000', u'm1500', u'm2000', u'm2500']  
    df_c = df.m5 > df.m10 and c > df.m5
    df_h = df.apply(lambda x:cn > x ,  axis = 1 )
    df_l = df.apply(lambda x:x.min() >= cl,  axis = 1 )
    
    df['dfh'] = df_h
    df['dfl'] = df_l
    df['code'] =code
#     out=df.iloc[-1].apply(lambda x: True if x>cl and x < ch else False)
    df=df.reset_index('tradeDate')
    df=df.set_index(['code','tradeDate'])
    return df

codes,data_df=readTdxLdayPath('data') #读取目录下面的所有文件
output=None
for code in codes:
  aaa=data_df.loc[code,]
  out=select1(code, aaa)
  if output is None:
    output = out
  else:
#     print(code)
    output=output.append(out)

output.to_csv('test.csv')