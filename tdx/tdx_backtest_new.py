import datetime
import QUANTAXIS as QA
from QAStrategy.qastockbase import QAStrategyStockBase
import random
from strategybase import StrategyBase
import numpy as np
import pandas as pd
from func.tdx_func import tdx_dhmcl, tdx_hm, tdx_sxp, tdx_hmdr
import math
deal_amount = 50000

def tdx_base_func(data, code_list = None):
    try:
        tdx_func_result, next_buy = tdx_dhmcl(data)
        # tdx_func_result, next_buy = tdx_hm(data)
        # tdx_func_result, next_buy = tdx_sxp(data)
        # tdx_func_result, next_buy = tdx_hmdr(data)
    # 斜率
    except:
        tdx_func_result, next_buy = False, False

    data = data.copy()
    data['B_FLG'] = tdx_func_result
    return data

# class SimpleBacktest01(QAStrategyStockBase):
class SimpleBacktest01(StrategyBase):
    def on_bar(self, bar):
        # res = self.ma()
        # print(res.iloc[-1])
        # if np.isnan(res.MA2[-1]) or np.isnan(res.MA5[-1]):
        #     return
        code=bar.name[1]
        # print(bar.name)
        # print("code=%s, ma2=%6.2f, m5=%6.2f" % (code, res.MA2[-1], res.MA5[-1]))
        # print(res)
        # print(self.get_positions(code))
        # if res.MA5[-1] > res.MA30[-1]:
        if bar['B_FLG']:
        # if res.DIF[-1] > res.DEA[-1]:

            # print('LONG price=%8.2f' % (bar['close']))
            price = bar['close']
            volume = math.floor(deal_amount / ( price * 100 )) * 100
            if self.get_positions(code).volume_long == 0 and volume > 0:
                self.send_order('BUY', 'OPEN', code=code, price=bar['close'], volume=volume)

            # if self.positions.volume_short > 0:
            #     self.send_order('BUY', 'CLOSE', code=code, price=bar['close'], volume=1)

        else:
            # print('SHORT price=%8.2f' % (bar['close']))

            # if self.acc.positions == {} or self.acc.positions.volume_short == 0:
            #     self.send_order('SELL', 'OPEN', code=code, price=bar['close'], volume=1)
            if self.get_positions(code).volume_long > 0:
                self.send_order('SELL', 'CLOSE', code=code, price=bar['close'], volume=1000)

    def ma(self,):
        return QA.QA_indicator_MA(self.market_data, 5, 30)
        # return QA.QA_indicator_MACD(self.market_data)

    def risk_check(self):
        pass

    def get_data(self):
        start_t = datetime.datetime.now()
        print("get_data-begin-time:", start_t)

        # data = self.mongo.get_stock_day(code, st_start=start)
        # data = data.sort_index()

        data = QA.QA_quotation(self.code, self.start, self.end, source=QA.DATASOURCE.MONGO,
                               frequence=self.frequence, market=self.market_type, output=QA.OUTPUT_FORMAT.DATASTRUCT)


        dataR = pd.DataFrame()
        datam = data.data.sort_index()
        for code in self.code:
            data = datam.query("code=='%s'" % code)
            tdx_func_result = tdx_base_func(data)
            if len(dataR) == 0:
                dataR = tdx_func_result
            else:
                dataR = dataR.append(tdx_func_result)

        end_t = datetime.datetime.now()
        print(end_t, 'get_data-spent:{}'.format((end_t - start_t)))
        return dataR.sort_index()

if __name__ == '__main__':
    start_t = datetime.datetime.now()
    print("begin-time:", start_t)
    codes_df = QA.QA_fetch_stock_list_adv()
    code_list = list(codes_df['code'])
    # print(code_list)
    # code = QA.QA_fetch_stock_block_adv().code
    # print(code)
    s = SimpleBacktest01(
                # code=['000001', '000002','600822','000859']
                code=code_list
                # code=QA.QA_fetch_stock_block_adv().code
                # , init_cash = 1000000000000
                , frequence='day'
                , start='2020-06-01', end='2020-12-31'
                , portfolio='example4'
                , strategy_id='super-simple-backtest13')
    # s.debug()
    s.run_backtest()
    # msg = s.acc.message
    # print("alpha=%6.2f, " % (msg['']))
    # s.update_account()
    end_t = datetime.datetime.now()
    print(end_t, 'spent:{}'.format((end_t - start_t)))

    risk = QA.QA_Risk(s.acc)
    # risk.plot_assets_curve().show()
    print(risk.annualize_return)
    print(risk.profit_construct)
  