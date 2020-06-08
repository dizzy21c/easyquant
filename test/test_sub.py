
from easyquant import EasyMq
from easyquant import MongoIo
import pandas as pd
from easyquant import base
# a = EasyMq()

# a.init_receive(exchange='stockcn')
# a.add_sub_key('000735')
# a.add_sub_key('000410')

# a.start()

from easyquant import MongoIo
m=MongoIo()
a=m.get_stock_day('000001')
a.date=pd.to_datetime(a.date)
b=a.set_index(['date'])


con1=base.BARSLAST(b.close>10)
print(con1.head())



