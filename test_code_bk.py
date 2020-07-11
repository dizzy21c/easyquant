from QUANTAXIS.QAFetch import QATdx as tdx

from easyquant import RedisIo
from easyquant.indicator.base import *
from easyquant.indicator.udf_formula import *

from pandas import Series,DataFrame
import pandas as pd
import numpy as np
rs=RedisIo()


code = '002007'
data_df = rs.get_day_df(code)
sin_data = rs.get_cur_data(code)
C=data_df.close

rs.get_day_ps(data_df, sin_data)

st_date="2019-06-05 14:30:00"
end_date="2019-06-05"
code="002107"
min=5
tdx.QA_fetch_get_stock_day(code, st_date,end_date)
md5=tdx.QA_fetch_get_stock_min(code, st_date,end_date, min)

row=md5.iloc[0]
data_dict={'code':code, 'open':row.open, 'high':row.high, 'low':row.low, 'date':row.date, 'now':row.close, 'turnover':row.vol * 100, 'volume':row.amount, 'datetime':row.datetime}
rs.push_min_data(row.code,data_dict,idx=0,min=min)



tdx.QA_fetch_get_stock_realtime(code)
tdx.QA_fetch_depth_market_data(code)
tdx.QA_fetch_get_stock_latest(code)
tdx.QA_fetch_get_stock_transaction_realtime(code)



rs=RedisIo()
data_df = rs.get_day_df('002007')
sdata = rs.get_cur_data('002007')
code="002107"
idx=0
data_df = rs.get_day_df(code)
sina_data = rs.get_cur_data(code, idx = idx)
O,C,H,L,V,A = rs.get_day_ps_ochlva(data_df, sina_data)

rs.calc_pct(H,O)

DIFF=EMA(C,12)-EMA(C,26)
DEA=EMA(DIFF,9)
MACD=2*(DIFF-DEA)

NS=BARSLAST(MACD<0)

SUMS(MACD,NS)
