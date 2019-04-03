from easyquant import StrategyTemplate


class Strategy(StrategyTemplate):
    name = 'test3'

    def strategy(self, event):
        self.log.info('\n\nStrategy 3 event')
        # self.log.info('data: stock-code-name %s' % event.data['162411'])
        # self.log.info('check balance')
        # self.log.info(self.user.balance)
        # self.log.info('\n')

