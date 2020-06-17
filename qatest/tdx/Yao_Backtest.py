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
    ma5 = QA.MA(close, 5)

    SC = base.CROSS(ma5, close)
    # CROSS_SC = base.CROSS(DEA, DIFF)
    # ZERO = 0
    res.SC = SC
    return res

class YaoBacktest(QAStrategyStockBase):
    def on_bar(self, data):
        code = data.name[1]
        # print(data)
        # print(self.get_positions('000001'))
        # print(self.market_data)
        #
        # code = data.name[1]
        # print('---------------under is 当前全市场的market_data --------------')
        #
        # print(self.get_current_marketdata())
        # print('---------------under is 当前品种的market_data --------------')
        # print(self.get_code_marketdata(code))
        # print(code)
        if len(self.get_code_marketdata(code)) < 21:
            return
        # code = data.name[1]
        res = self.macd(code)
        # sig = QA.CROSS(res.KDJ_J, res.KDJ_K)
        # sig2 = QA.CROSS(res.KDJ_K, res.KDJ_J)
        # print(res.iloc[-1])
        # if np.isnan(res.MA2[-1]) or np.isnan(res.MA5[-1]):
        #     return
        # code=bar.name[1]
        # print(bar.name)
        # print("code=%s, ma2=%6.2f, m5=%6.2f" % (code, res.MA2[-1], res.MA5[-1]))
        # print(res)
        # print(self.get_positions(code))
        # if res.MA5[-1] > res.MA30[-1]:
        # print("sig1=%6.2f, sig2=%6.2f" % (sig[-1], sig2[-1]))
        if res.FLTP[-1] or res.FLCS[-1]:
        # if res.DIF[-1] > res.DEA[-1]:

            # print('LONG price=%8.2f' % (bar['close']))

            if self.get_positions(code).volume_long == 0:
                self.send_order('BUY', 'OPEN', code=code, price=data['close'], volume=1000)

            # if self.positions.volume_short > 0:
            #     self.send_order('BUY', 'CLOSE', code=code, price=bar['close'], volume=1)

        elif res.SC[-1] > 0:
            # print('SHORT price=%8.2f' % (bar['close']))

            # if self.acc.positions == {} or self.acc.positions.volume_short == 0:
            #     self.send_order('SELL', 'OPEN', code=code, price=bar['close'], volume=1)
            if self.get_positions(code).volume_long > 0:
                self.send_order('SELL', 'CLOSE', code=code, price=data['close'], volume=1000)

    def macd(self,code):
        # res = data.add_func(QA.QA_indicator_KDJ)
        # sig = QA.CROSS(res.KDJ_J, res.KDJ_K)
        # sig2 = QA.CROSS(res.KDJ_K, res.KDJ_J)
        return YAO_FN(self.get_code_marketdata(code))
        # res = QA.QA_indicator_KDJ(self.market_data)
        # return res
        # return QA.QA_indicator_MACD(self.market_data)

    def risk_check(self):
        pass

if __name__ == '__main__':
    s = YaoBacktest(
                code=['600822']
                # code=QA.QA_fetch_stock_block_adv().code[0:10]
                # , frequence='30min'
                , frequence='day'
                , start='2020-01-01', end='2020-12-31'
                , portfolio='example'
                , strategy_id='super-simple_MACD-day')
    # s.debug()
    s.run_backtest()
    # msg = s.acc.message
    # print("alpha=%6.2f, " % (msg['']))
    # s.update_account()

    risk = QA.QA_Risk(s.acc)
    # risk.plot_assets_curve().show()
    print(risk.profit_construct)

  