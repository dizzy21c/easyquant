from easyquant import QATdx as tdx
from easyquant import RedisIo
from easyquant.indicator.base import *
from easyquant.indicator.udf_formula import *

from pandas import Series,DataFrame
import pandas as pd
import numpy as np

rs=RedisIo()

data_df = rs.get_day_df('002007')
C=data_df.close

st_date="2019-06-05"
end_date="2019-06-05"
code="002007"
tdx.QA_fetch_get_stock_day(code, st_date,end_date)

tdx.QA_fetch_get_stock_realtime(code)
tdx.QA_fetch_depth_market_data(code)
tdx.QA_fetch_get_stock_latest(code)
tdx.QA_fetch_get_stock_transaction_realtime(code)

