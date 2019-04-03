import easyquotation
import datetime
import json
import easyquant
from easyquant import DefaultQuotationEngine, DefaultLogHandler, PushBaseEngine
import pymongo
# print('easyquant 测试 DEMO')
# print('请输入你使用的券商:')
# choose = input('1: 华泰 2: 佣金宝 3: 银河 4: 雪球模拟组合 5: 广发\n:')

broker = None
# if choose == '2':
#     broker = 'yjb'
# elif choose == '3':
#     broker = 'yh'
# elif choose == '4':
#     broker = 'xq'
# elif choose == '5':
#     broker = 'gf'


# def get_broker_need_data(choose_broker):
#     need_data = input('请输入你的帐号配置文件路径(直接回车使用 %s.json)\n:' % choose_broker)
#     if need_data == '':
#         return '%s.json' % choose_broker
#     return need_data


need_data = '' #get_broker_need_data(broker)


class SinaEngine(PushBaseEngine):
    EventType = 'sina'

    def init(self):
        self.source = easyquotation.use('sina')

    def fetch_quotation(self):
        #print("fetch %s " % datetime.datetime.now())
        out = self.source.market_snapshot(prefix=True) 
        return out

    def fetch_quotation2(self):
        config_name = './config/chklist.json'
        with open(config_name, 'r') as f:
            data = json.load(f)
            out = self.source.stocks(data['pos'])
            # print (out)
            while len(out) == 0:
                out = self.source.stocks(data['pos'])
            # print (out)
            return out
            # return self.source.stocks(data['pos'])

class LFEngine(PushBaseEngine):
    EventType = 'lf'

    def init(self):
        self.source = easyquotation.use('lf')

    def fetch_quotation(self):
        # print ('ok...')
        config_name = './config/chklist.json'
        with open(config_name, 'r') as f:
            data = json.load(f)
            out = self.source.stocks(data['pos'])
            while len(out) == 0:
                out = self.source.stocks(data['pos'])
            print ("dataout:" + len(out))
            return out
            # return self.source.stocks(data['pos'])


# quotation_choose = input('Please input engine 1: sina 2: leverfun \n:')

# quotation_engine = DefaultQuotationEngine if quotation_choose == '1' else LFEngine
quotation_engine = SinaEngine
# quotation_engine = LFEngine

#push_interval = int(input('please input interval(s)\n:'))
push_interval = 10
quotation_engine.PushInterval = push_interval

# log_type_choose = '2' #input('请输入 log 记录方式: 1: 显示在屏幕 2: 记录到指定文件\n: ')
log_type = 'file'#'stdout' if log_type_choose == '1' else 'file'

log_filepath = 'logs/log.txt' #input('请输入 log 文件记录路径\n: ') if log_type == 'file' else ''

log_handler = DefaultLogHandler(name='strategy', log_type=log_type, filepath=log_filepath)

client= pymongo.MongoClient('localhost',27017)
db = client.quantaxis

m = easyquant.MainEngine(broker, need_data, quotation_engines=[quotation_engine], log_handler=log_handler, mdb=db)
m.is_watch_strategy = True  # 策略文件出现改动时,自动重载,不建议在生产环境下使用
m.load_strategy()
m.start()
