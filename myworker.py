import easyquotation
import datetime
import json
import easyquant
from easyquant import DefaultQuotationEngine, DefaultLogHandler, PushBaseEngine
from custom.sinadataengine import SinaEngine
import sys
#import pymongo
#import redis
# print('easyquant 测试 DEMO')
# print('trader:')
# choose = input('1: \n:')

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

class WorkerEngine(SinaEngine):
    EventType = 'worker'
    PushInterval = 10

# worker_engine = DataEngine
# worker_engine.EventType = "worker"
# worker_engine.PushInterval = 10
# worker_engine.config = "worker"

# quotation_choose = input('Please input engine 1: sina 2: leverfun \n:')

# quotation_engine = DefaultQuotationEngine if quotation_choose == '1' else LFEngine

#data_engine = DataSinaEngine
#index_engine = IndexSinaEngine
#worker_engine = WorkerEngine

# quotation_engine = LFEngine

#push_interval = int(input('please input interval(s)\n:'))
#push_interval = 10
#data_engine.PushInterval = push_interval
#index_engine.PushInterval = push_interval
#worker_engine.PushInterval = push_interval

# log_type_choose = '2' #input('请输入 log 记录方式: 1: 显示在屏幕 2: 记录到指定文件\n: ')
_logname="worker"
_log_type = 'file'#'stdout' if log_type_choose == '1' else 'file'
_log_filepath = 'logs/%s.txt' % _logname #input('请输入 log 文件记录路径\n: ') if log_type == 'file' else ''
log_handler = DefaultLogHandler(name=_logname, log_type=_log_type, filepath=_log_filepath)

#client= pymongo.MongoClient('localhost',27017)
#db = client.quantaxis
#rdb = redis.Redis(host='localhost', port=6379, db=0)
#print(rdb)
#m = easyquant.MainEngine(broker, need_data, quotation_engines=[quotation_engine], log_handler=log_handler)
# qe_list=[data_engine, IndexSinaEngine, WorkerEngine]
#qe_list=[DataSinaEngine, IndexSinaEngine, BlockSinaEngine, WorkerEngine]

qe_list=[WorkerEngine]
m = easyquant.MainEngine(broker, need_data, quotation_engines=qe_list, log_handler=log_handler)
m.is_watch_strategy = False  # 策略文件出现改动时,自动重载,不建议在生产环境下使用
names=None
if len(sys.argv) > 1:
    names = [sys.argv[1]]
m.load_strategy(names=names)
m.start()
