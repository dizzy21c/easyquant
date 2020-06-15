import QUANTAXIS as QA
from QAStrategy.qastockbase import QAStrategyStockBase
import numpy as np


class strategy(QAStrategyStockBase):
    def on_bar(self, bar):
        res = self.ma()
        # print(res.iloc[-1])
        # if np.isnan(res.MA2[-1]) or np.isnan(res.MA5[-1]):
        #     return
        code=bar.name[1]
        # print(bar.name)
        # print("code=%s, ma2=%6.2f, m5=%6.2f" % (code, res.MA2[-1], res.MA5[-1]))
        # print(res)
        # print(self.get_positions(code))
        if res.MA5[-1] > res.MA30[-1]:
        # if res.DIF[-1] > res.DEA[-1]:

            # print('LONG price=%8.2f' % (bar['close']))

            if self.get_positions(code).volume_long == 0:
                self.send_order('BUY', 'OPEN', code=code, price=bar['close'], volume=100)

            # if self.positions.volume_short > 0:
            #     self.send_order('BUY', 'CLOSE', code=code, price=bar['close'], volume=1)

        else:
            # print('SHORT price=%8.2f' % (bar['close']))

            # if self.acc.positions == {} or self.acc.positions.volume_short == 0:
            #     self.send_order('SELL', 'OPEN', code=code, price=bar['close'], volume=1)
            if self.get_positions(code).volume_long > 0:
                self.send_order('SELL', 'CLOSE', code=code, price=bar['close'], volume=100)

    def ma(self,):
        return QA.QA_indicator_MA(self.market_data, 5, 30)
        # return QA.QA_indicator_MACD(self.market_data)

    def risk_check(self):
        pass

if __name__ == '__main__':
    s = strategy(code=['000001', '000002','600822','000859'], frequence='day', start='2020-01-01', end='2020-12-31', strategy_id='stock-test')
    # s.debug()
    s.run_backtest()
    # msg = s.acc.message
    # print("alpha=%6.2f, " % (msg['']))
    # s.update_account()
  