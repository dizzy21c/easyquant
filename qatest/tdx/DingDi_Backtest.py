import QUANTAXIS as QA
from QAStrategy.qastockbase import QAStrategyStockBase
from easyquant.indicator.base import *
from easyquant.indicator.udf_formula import *

import pandas as pd
import random

import numpy as np

def CALC_FUN(data, SHORT=12, LONG=26, M=9):
    # """
    # 1.DIF向上突破DEA，买入信号参考。
    # 2.DIF向下跌破DEA，卖出信号参考。
    # """
    C = data.close
    H = data.high
    L = data.low
    H1 = MAX(REF(C, 1), H)
    L1 = MIN(REF(C, 1), L)
    P1 = H1 - L1
    ZL = L1 + P1 * 7 / 8
    ZC = L1 + P1 * 0.5 / 8
    ZX = (ZC + ZL) / 2
    V11 = 3 * SMA((C - LLV(L, 55)) / (HHV(H, 55) - LLV(L, 55)) * 100, 5, 1) - 2 * SMA(SMA((C - LLV(L, 55)) / (HHV(H, 55) - LLV(L, 55)) * 100, 5, 1), 3, 1)
    QSX = EMA(V11, 3)
    # V12 = (QSX - REF(QSX, 1)) / REF(QSX, 1) * 100
    BB01 = IFAND(REF(QSX, 1) < 11 , CROSS(QSX, 11) , True, False)
    print(BB01.index[-1])
    BB0 = IFAND(BB01, C < ZX, True, False)
    BB11 = IFAND(REF(QSX, 1) < 11, REF(QSX, 1) > 6, True, False)
    BB1 = IFAND(BB11 , CROSS(QSX, 11), True, False)
    BB21 = IFAND(REF(QSX, 1) < 6 , REF(QSX, 1) > 3, True, False)
    BB2 = IFAND(BB21 , CROSS(QSX, 6), True, False)
    BB31 = IFAND(REF(QSX, 1) < 3 , REF(QSX, 1) > 1, True, False)
    BB3 = IFAND(BB31 , CROSS(QSX, 3) , True, False)
    BB41 = IFAND(REF(QSX, 1) < 1 , REF(QSX, 1) > 0, True, False)
    BB4 = IFAND(BB41 , CROSS(QSX, 1) , True, False)
    BB5 = IFAND(REF(QSX, 1) < 0 , CROSS(QSX, 0), True, False)

    BBA1 = IFOR(BB0 ,BB1 ,True,False)
    BBA2 = IFOR(BB2 ,BB3 ,True,False)
    BBA3 = IFOR(BB4, BB5, True, False)

    BBA4 = IFOR(BBA1, BBA2, True, False)
    BBA5 = IFOR(BBA3, BBA4, True, False)

    BB = IFOR(BBA4, BBA5, True, False)
    BUY1 = IFAND(BB, C < ZX, True, False)

    DD01 = IFAND(REF(QSX, 1) > 89 , CROSS(89, QSX) , True, False)
    DD0 = IFAND(DD01 , C > ZX , True, False)
    DD11 = IFAND(REF(QSX, 1) > 89 , REF(QSX, 1) < 94 , True, False)
    DD1 = IFAND(DD11 , CROSS(89, QSX), True, False)
    DD21 = IFAND(REF(QSX, 1) > 94 , REF(QSX, 1) < 97 , True, False)
    DD2 = IFAND(DD21 , CROSS(94, QSX) , True, False)
    DD31 = IFAND(REF(QSX, 1) > 97 , REF(QSX, 1) > 99 , True, False)
    DD3 = IFAND(DD31 , CROSS(97, QSX) , True, False)
    DD41 = IFAND(REF(QSX, 1) > 99 , REF(QSX, 1) < 100 , True, False)
    DD4 = IFAND(DD41 , CROSS(99, QSX) , True, False)
    DD5 = IFAND(REF(QSX, 1) > 100 , CROSS(100, QSX), True, False)

    DDA1 = IFOR(DD0 ,DD1 ,True,False)
    DDA2 = IFOR(DD2 ,DD3 ,True,False)
    DDA3 = IFOR(DD4, DD5, True, False)

    DDA4 = IFOR(DDA1, DDA2, True, False)
    DDA5 = IFOR(DDA3, DDA4, True, False)

    DD = IFOR(DDA5, DD5, True, False)
    SELL1 = IFAND(DD, C > ZX, True, False)

    # ma5=base.REF(base.MA(data.close, 5),1)
    # ma20=base.REF(base.MA(data.close, 20),1)
    data['BUY'] = BUY1
    data['SELL'] = SELL1
    # # res = udf_yao_check_df(dataframe)
    # res = udf_yao_check(data.close, data.open, data.high, data.low, data.volume)
    # close = data.close
    # ma5 = base.MA(close, 5)
    #
    # sc = base.CROSS(ma5, close)
    # # CROSS_SC = base.CROSS(DEA, DIFF)
    # # ZERO = 0
    # res['SC'] = sc
    return data

class MaBacktest(QAStrategyStockBase):
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
        res = self.calc(code)
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
        if res.BUY[-1]: # or res.BUY2[-1]:
        # if res.DIF[-1] > res.DEA[-1]:

            # print('LONG price=%8.2f' % (bar['close']))

            if self.get_positions(code).volume_long == 0:
                self.send_order('BUY', 'OPEN', code=code, price=data['close'], volume=1000)

            # if self.positions.volume_short > 0:
            #     self.send_order('BUY', 'CLOSE', code=code, price=bar['close'], volume=1)

        elif res.SELL[-1] > 0:
            # print('SHORT price=%8.2f' % (bar['close']))

            # if self.acc.positions == {} or self.acc.positions.volume_short == 0:
            #     self.send_order('SELL', 'OPEN', code=code, price=bar['close'], volume=1)
            if self.get_positions(code).volume_long > 0:
                self.send_order('SELL', 'CLOSE', code=code, price=data['close'], volume=1000)

    def calc(self,code):
        # res = data.add_func(QA.QA_indicator_KDJ)
        # sig = QA.CROSS(res.KDJ_J, res.KDJ_K)
        # sig2 = QA.CROSS(res.KDJ_K, res.KDJ_J)
        data=self.get_code_marketdata(code)
        print(data.index.names)
        return CALC_FUN(self.get_code_marketdata(code))
        # res = QA.QA_indicator_KDJ(self.market_data)
        # return res
        # return QA.QA_indicator_MACD(self.market_data)

    def risk_check(self):
        pass

if __name__ == '__main__':
    s = MaBacktest(
                code=['600821']
                # code=QA.QA_fetch_stock_block_adv().code[0:10]
                # , frequence='30min'
                , frequence='day'
                , start='2019-01-01', end='2020-12-31'
                , portfolio='example'
                , strategy_id='DingDi-day')
    # s.debug()
    s.run_backtest()
    # msg = s.acc.message
    # print("alpha=%6.2f, " % (msg['']))
    # s.update_account()

    risk = QA.QA_Risk(s.acc)
    risk.plot_assets_curve().show()
    print(risk.profit_construct)

  