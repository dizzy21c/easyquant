import datetime
import pandas as pd
import random

from strategybase import StrategyBase
from multiprocessing import Process, Pool, cpu_count, Manager
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor,as_completed
from QUANTAXIS.QAARP import QA_Risk, QA_User
import QUANTAXIS as QA

executor = ProcessPoolExecutor(max_workers=cpu_count())


class TdxBacktest(StrategyBase):
    def on_bar2(self, bar):
        # print("on-bar333", bar)
        pass

    def on_bar(self, bar):
        # res = self.ma()
        # print(bar.name)
        # if np.isnan(res.MA2[-1]) or np.isnan(res.MA5[-1]):
        #     return
        code=bar.name[1]
        # print(bar.name)
        # print("code=%s, ma2=%6.2f, m5=%6.2f" % (code, res.MA2[-1], res.MA5[-1]))
        # print(res)
        # print(self.get_positions(code))
        # if res.MA5[-1] > res.MA30[-1]:
        if random.random() > 0.5:
            # print('LONG price=%8.2f' % (bar['close']))

            if self.get_positions(code).volume_long == 0:
                self.send_order('BUY', 'OPEN', code=code, price=bar['close'], volume=1000)
                print(bar.name[0], 'code=%s, BUY price=%8.2f ' % (code, bar['close']))
        else:
            # print('SHORT price=%8.2f' % (bar['close']))
            # if self.acc.positions == {} or self.acc.positions.volume_short == 0:
            #     self.send_order('SELL', 'OPEN', code=code, price=bar['close'], volume=1)
            if self.get_positions(code).volume_long > 0:
                self.send_order('SELL', 'CLOSE', code=code, price=bar['close'], volume=1000)
                print(bar.name[0], 'code=%s, SELL price=%8.2f' % (code, bar['close']))

    def get_sub_data(self, code_list, start):
        return self.mongo.get_stock_day(code_list, st_start=start)

    def get_data(self, code, start, end):
        start_t = datetime.datetime.now()
        print("get_data-begin-time:", start_t)

        data = self.mongo.get_stock_day(code, st_start=start)
        data = data.sort_index()
        end_t = datetime.datetime.now()
        print(end_t, 'get_data-spent:{}'.format((end_t - start_t)))

        return data

    def get_data2(self, code, start, end):
        # df = pd.DataFrame()
        if isinstance(code, str):
            # df = pd.DataFrame()
            data = self.mongo.get_stock_day(code, st_start=start)
            return data.sort_index()
        else:
            codelist = code
            pool_size = cpu_count()
            task_list = []
            if (len(codelist)) < 20:
                data = self.mongo.get_stock_day(code, st_start=start)
                return data.sort_index()

            subcode_len = int(len(codelist) / pool_size)
            for i in range(pool_size):
                if i < pool_size - 1:
                    sub_code_list = codelist[i * subcode_len: (i + 1) * subcode_len]
                else:
                    sub_code_list = codelist[i * subcode_len:]
                task_list.append(executor.submit(self.get_sub_data, sub_code_list, start))

            dataR = pd.DataFrame()
            for task in as_completed(task_list):
                if len(dataR) == 0:
                    dataR = task.result()
                else:
                    dataR = dataR.append(task.result())

            return dataR.sort_index()

if __name__ == '__main__':
    start_t = datetime.datetime.now()
    print("begin-time:", start_t)
    # code_list = ['600718', '600756']
    codes_df = QA.QA_fetch_stock_list_adv()
    code_list = list(codes_df['code'])

    s = TdxBacktest(code=code_list[0:5], start='2020-08-20', end='2020-05-21'
                    , init_cash=1000000
                    , portfolio='default2'
                    , strategy_id='QA_STRATEGY2')

    s.run_backtest()

    end_t = datetime.datetime.now()
    print(end_t, 'spent:{}'.format((end_t - start_t)))

    risk = QA_Risk(s.acc)
    risk.plot_assets_curve().show()
    print(risk.profit_construct)

