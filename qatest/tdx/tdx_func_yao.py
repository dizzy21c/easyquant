import QUANTAXIS as QA
from QAStrategy.qastockbase import QAStrategyStockBase
from easyquant.indicator import base
from easyquant.indicator.udf_formula import *

import pandas as pd
import random
import numpy as np

def YAO_FN(data, SHORT=12, LONG=26, M=9):
    """
    1.DIF向上突破DEA，买入信号参考。
    2.DIF向下跌破DEA，卖出信号参考。
    """
    # res = udf_yao_check_df(dataframe)
    res = udf_yao_check(data.close, data.open, data.high, data.low, data.volume)
    close = data.close
    ma5 = base.MA(close, 5)

    sc = base.CROSS(ma5, close)
    # CROSS_SC = base.CROSS(DEA, DIFF)
    # ZERO = 0
    res['SC'] = sc
    return res