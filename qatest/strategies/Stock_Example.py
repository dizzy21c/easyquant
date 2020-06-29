import QUANTAXIS as QA
from QAStrategy.qastockbase import QAStrategyStockBase



class strategy(QAStrategyStockBase):
    def on_bar(self, data):
        # print(data)
        # print(self.get_positions('000001'))
        # print(self.market_data)
        #
        code = data.name[1]
        # print('---------------under is 当前全市场的market_data --------------')
        #
        print(self.get_current_marketdata())
        # print('---------------under is 当前品种的market_data --------------')
        print(self.get_code_marketdata(code))
        print(data.name)
        #print(self.running_time)
        input()

if __name__ == '__main__':
    codelist=QA.QA_fetch_stock_block_adv().code[0:5]
    s = strategy(code=codelist, frequence='day', start='2019-01-01', end='2019-02-01', strategy_id='x')
    s.run_backtest()