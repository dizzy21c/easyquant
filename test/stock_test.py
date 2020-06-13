import QUANTAXIS as QA
from QAStrategy.qastockbase import QAStrategyStockBase
import numpy as np


class strategy(QAStrategyStockBase):
    def on_bar(self, bar):
        res = self.ma()
        # print(res.iloc[-1])
        if np.isnan(res.MA2[-1]) or np.isnan(res.MA5[-1]):
            return

        if res.MA2[-1] > res.MA5[-1]:

            print('LONG price=%8.2f' % (bar['close']))

            if self.positions.volume_long == 0:
                self.send_order('BUY', 'OPEN', price=bar['close'], volume=1)

            if self.positions.volume_short > 0:
                self.send_order('BUY', 'CLOSE', price=bar['close'], volume=1)

        else:
            print('SHORT price=%8.2f' % (bar['close']))

            if self.positions.volume_short == 0:
                self.send_order('SELL', 'OPEN', price=bar['close'], volume=1)
            if self.positions.volume_long > 0:
                self.send_order('SELL', 'CLOSE', price=bar['close'], volume=1)

    def ma(self,):
        return QA.QA_indicator_MA(self.market_data, 2, 5)

    def risk_check(self):
        pass

if __name__ == '__main__':
    s = strategy(code=['000001', '000002','600822','000859'], frequence='day', start='2020-01-01', end='2020-12-31', strategy_id='stock-test')
    # s.debug()
    s.run_backtest()
    # s.update_account()
  