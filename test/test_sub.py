
from easyquant import EasyMq
from easyquant import MongoIo
# a = EasyMq()

# a.init_receive(exchange='stockcn')
# a.add_sub_key('000735')
# a.add_sub_key('000410')

# a.start()


m=MongoIo()

m.get_stock_day('000001')