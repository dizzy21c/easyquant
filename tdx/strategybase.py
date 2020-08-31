import uuid

import datetime, time
from QUANTAXIS.QAARP import QA_Risk, QA_User
import QUANTAXIS as QA
from QUANTAXIS.QAUtil.QAParameter import MARKET_TYPE, RUNNING_ENVIRONMENT, ORDER_DIRECTION

import pandas as pd
from easyquant import MongoIo


class StrategyBase():
    def __init__(self, code='000001', frequence='day', strategy_id='QA_STRATEGY', risk_check_gap=1, portfolio='default',
                 start='2020-01-01', end='2020-05-21', init_cash=1000000, send_wx=False,
                 data_user='admin', data_password='admin',
                 # trade_host=eventmq_ip, trade_port=eventmq_port, trade_user=eventmq_username, trade_password=eventmq_password,
                 taskid=None):
        self.username = data_user
        self.password = data_password
        self._market_data = []

        self.code = code
        self.frequence = frequence
        self.strategy_id = strategy_id

        self.portfolio = portfolio

        self.start = start
        self.end = end
        self.init_cash = init_cash
        self.taskid = taskid

        self.risk_check_gap = risk_check_gap

        self.mongo = MongoIo()

        if isinstance(self.code, str):
            self.market_type = 'stock_cn'
        else:
            self.market_type = 'stock_cn'

        self.bar_order = {'BUY_OPEN': 0, 'SELL_OPEN': 0,
                          'BUY_CLOSE': 0, 'SELL_CLOSE': 0}

        self.running_time = ''

    def run_backtest(self):
        self.debug()
        # self.acc.save()
        #
        # risk = QA_Risk(self.acc)
        # risk.save()
        #
        # try:
        #     """add rank flow if exist
        #
        #     QARank是我们内部用于评价策略ELO的库 此处并不影响正常使用
        #     """
        #     from QARank import QA_Rank
        #     QA_Rank(self.acc).send()
        # except:
        #     pass
    def on_bar(self, bar):
        raise NotImplementedError
        # print("on-bar", bar)
        # pass

    def x1(self, item):
        # self.latest_price[item.name[1]] = item['close']
        # if str(item.name[0])[0:10] != str(self.running_time)[0:10]:
        #     self.on_dailyclose()
        #     self.on_dailyopen()
        #     if self.market_type == QA.MARKET_TYPE.STOCK_CN:
        #         print('backtest: Settle!')
        #         self.acc.settle()
        # self._on_1min_bar()
        self._market_data.append(item)
        self.running_time = str(item.name[0])
        self.on_bar(item)

    def debug(self):
        self.running_mode = 'backtest'
        # self.database = pymongo.MongoClient(mongo_ip).QUANTAXIS
        user = QA_User(username="admin", password='admin')
        port = user.new_portfolio(self.portfolio)
        self.acc = port.new_accountpro(
            account_cookie=self.strategy_id, init_cash=self.init_cash, market_type=self.market_type, frequence= self.frequence)
        #self.positions = self.acc.get_position(self.code)

        print(self.acc)

        print(self.acc.market_type)
        data = self.get_data(self.code, self.start, self.end)

        data.apply(self.x1, axis=1)

    def get_data(self, codelist, start, end):
        raise NotImplementedError

    def risk_check(self):
        print("risk check")
        # pass

    def run(self):

        while True:
            time.sleep(self.risk_check_gap)
            self.risk_check()
    @property
    def bar_id(self):
        return len(self._market_data)

    @property
    def market_data(self):

        if self.running_mode == 'sim':
            return self._market_data
        elif self.running_mode == 'backtest':
            return pd.concat(self._market_data[-100:], axis=1, sort=False).T

    def send_order(self,  direction='BUY', offset='OPEN', code=None, price=3925, volume=10, order_id='',):

        towards = eval('ORDER_DIRECTION.{}_{}'.format(direction, offset))
        order_id = str(uuid.uuid4()) if order_id == '' else order_id

        if self.market_type == QA.MARKET_TYPE.STOCK_CN:
            """
            在此对于股票的部分做一些转换
            """
            if towards == ORDER_DIRECTION.SELL_CLOSE:
                towards = ORDER_DIRECTION.SELL
            elif towards == ORDER_DIRECTION.BUY_OPEN:
                towards = ORDER_DIRECTION.BUY

        if isinstance(price, float):
            pass
        elif isinstance(price, pd.Series):
            price = price.values[0]

        # if self.running_mode == 'sim':
        #
        #     QA.QA_util_log_info(
        #         '============ {} SEND ORDER =================='.format(order_id))
        #     QA.QA_util_log_info('direction{} offset {} price{} volume{}'.format(
        #         direction, offset, price, volume))
        #
        #     if self.check_order(direction, offset):
        #         self.last_order_towards = {'BUY': '', 'SELL': ''}
        #         self.last_order_towards[direction] = offset
        #         now = str(datetime.datetime.now())
        #
        #         order = self.acc.send_order(
        #             code=code, towards=towards, price=price, amount=volume, order_id=order_id)
        #         order['topic'] = 'send_order'
        #         self.pub.pub(
        #             json.dumps(order), routing_key=self.strategy_id)
        #
        #         self.acc.make_deal(order)
        #         self.bar_order['{}_{}'.format(direction, offset)] = self.bar_id
        #         if self.send_wx:
        #             for user in self.subscriber_list:
        #                 QA.QA_util_log_info(self.subscriber_list)
        #                 try:
        #                     "oL-C4w2WlfyZ1vHSAHLXb2gvqiMI"
        #                     """http://www.yutiansut.com/signal?user_id=oL-C4w1HjuPRqTIRcZUyYR0QcLzo&template=xiadan_report&\
        #                                 strategy_id=test1&realaccount=133496&code=rb1910&order_direction=BUY&\
        #                                 order_offset=OPEN&price=3600&volume=1&order_time=20190909
        #                     """
        #
        #                     requests.post('http://www.yutiansut.com/signal?user_id={}&template={}&strategy_id={}&realaccount={}&code={}&order_direction={}&order_offset={}&price={}&volume={}&order_time={}'.format(
        #                         user, "xiadan_report", self.strategy_id, self.acc.user_id, code, direction, offset, price, volume, now))
        #                 except Exception as e:
        #                     QA.QA_util_log_info(e)
        #
        #     else:
        #         QA.QA_util_log_info('failed in ORDER_CHECK')

        # elif self.running_mode == 'backtest':
        if self.running_mode == 'backtest':
            self.bar_order['{}_{}'.format(direction, offset)] = self.bar_id

            self.acc.receive_simpledeal(
                code=code, trade_time=self.running_time, trade_towards=towards, trade_amount=volume, trade_price=price, order_id=order_id)
            #self.positions = self.acc.get_position(self.code)

    def get_positions(self, code):
        if self.running_mode == 'sim':
            self.update_account()
            return self.acc.get_position(code)
        elif self.running_mode == 'backtest':
            return self.acc.get_position(code)


if __name__ == '__main__':
    start_t = datetime.datetime.now()
    print("begin-time:", start_t)

    s = StrategyBase(code = ['600718', '600756'])

    s.run_backtest()

    end_t = datetime.datetime.now()
    print(end_t, 'spent:{}'.format((end_t - start_t)))
