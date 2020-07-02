import easyquotation
import datetime
import json
import easyquant
from easyquant import DefaultQuotationEngine, DefaultLogHandler, PushBaseEngine
from custom.fixedmainengine import FixedMainEngine
from custom.sinadataengine import SinaEngine
#import pymongo
#import redis
# choose = input('1: \n:')
import click

broker = None

need_data = '' #get_broker_need_data(broker)

class DataSinaEngine(SinaEngine):
    EventType = 'data-sina'
    PushInterval = 5
    config = "stock_calc_list"

@click.command ()
@click.option ('--log-name', default="SAME_NAME", help = 'log-name')
@click.option('--calc-name', default = "calc-day-data", help= 'calc-name[calc-day-data, calc-min-data,calc-day-data-idx]')
def startWork(calc_name, log_name):
    # log_type_choose = '2' #input('请输入 log 记录方式: 1: 显示在屏幕 2: 记录到指定文件\n: ')
    log_type = 'file'#'stdout' if log_type_choose == '1' else 'file'

    if log_name == 'SAME_NAME':
        log_filepath = 'logs/%s.txt' % calc_name
    else:
        log_filepath = 'logs/%s.txt' % log_name

    log_handler = DefaultLogHandler(name='calc-data', log_type=log_type, filepath=log_filepath)
    qe_list=[DataSinaEngine]
    m = easyquant.MainEngine(broker, need_data, quotation_engines=qe_list, log_handler=log_handler)
    # m = FixedMainEngine(broker, need_data, quotation_engines=qe_list, log_handler=log_handler)
    m.is_watch_strategy = False #True  # 策略文件出现改动时,自动重载,不建议在生产环境下使用
    names=[calc_name]
    m.load_strategy(names=names)
    m.start()

if __name__ == "__main__":
    startWork()
