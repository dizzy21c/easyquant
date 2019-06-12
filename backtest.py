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

need_data = '' #get_broker_need_data(broker)

class WorkerEngine(SinaEngine):
    EventType = 'worker'
    PushInterval = 1

_logname="bt-worker"
_log_type = 'file'#'stdout' if log_type_choose == '1' else 'file'
_log_filepath = 'logs/bt-mainlog.txt' # % _logname #input('请输入 log 文件记录路径\n: ') if log_type == 'file' else ''
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
m.backtest()
