
from easyquant import EasyMq
from easyquant import MongoIo
import pandas as pd
from easyquant import base
import talib as tdx
# import pandas as pd

# a = EasyMq()

# a.init_receive(exchange='stockcn')
# a.add_sub_key('000735')
# a.add_sub_key('000410')

# a.start()

from easyquant import MongoIo
m=MongoIo()
a=m.get_stock_day('000001')
# a.date=pd.to_datetime(a.date)
# b=a.set_index(['date'])


con1=base.BARSLAST(b.close>10)
print(con1.head())

df=pd.concat([tdx.MA(df_day.close, x) for x in (5,10,20,30,60,90,120,250,13, 34, 55,) ], axis = 1)[-1:]
df.columns = [u'm5',u'm10',u'm20',u'm30',u'm60',u'm90',u'm120', u'm250', u'm13', u'm34', u'm55']

print(df.m5.iloc[-1])





